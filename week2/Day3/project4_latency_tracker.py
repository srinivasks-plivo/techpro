"""
Project 4: Measure and Optimize Latency
========================================
Adds latency tracking to the voice bot to measure end-to-end response time.

Latency is measured from:
    - User stops speaking (VADUserStoppedSpeakingFrame) -> First TTS audio (TTSStartedFrame)

This captures the full STT + LLM + TTS pipeline latency.

Pipeline:
    Microphone -> LatencyStart -> STT -> User Aggregator -> LLM -> TTS
    -> LatencyEnd -> Speaker -> Assistant Aggregator

Usage:
    python project4_latency_tracker.py

    # Compare with GPT-4o (instead of GPT-4.1-mini):
    python project4_latency_tracker.py --model gpt-4o

Verification:
    1. Run multiple conversations and note average latency
    2. Compare GPT-4.1-mini vs GPT-4o latency
    3. Target: under 1.5 seconds end-to-end
"""

import argparse
import asyncio
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import (
    Frame,
    TTSSpeakFrame,
    TTSStartedFrame,
    UserStoppedSpeakingFrame,
    VADUserStoppedSpeakingFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


class LatencyTracker(FrameProcessor):
    """Custom processor that measures end-to-end voice latency.

    Tracks the time between when the user stops speaking and when the
    first TTS audio starts playing. This captures the full pipeline
    latency: STT processing + LLM inference + TTS generation.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._user_stop_time = None
        self._latencies = []
        self._exchange_count = 0

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        # Detect when user stops speaking
        if isinstance(frame, (UserStoppedSpeakingFrame, VADUserStoppedSpeakingFrame)):
            self._user_stop_time = time.perf_counter()
            logger.info("LATENCY: User stopped speaking")

        # Detect when first TTS audio starts
        if isinstance(frame, TTSStartedFrame) and self._user_stop_time is not None:
            latency = time.perf_counter() - self._user_stop_time
            self._exchange_count += 1
            self._latencies.append(latency)
            avg_latency = sum(self._latencies) / len(self._latencies)

            logger.info(
                f"LATENCY: Exchange #{self._exchange_count} | "
                f"This: {latency:.3f}s | "
                f"Avg: {avg_latency:.3f}s | "
                f"Min: {min(self._latencies):.3f}s | "
                f"Max: {max(self._latencies):.3f}s"
            )
            self._user_stop_time = None

        # Pass the frame through unchanged
        await self.push_frame(frame, direction)


async def main():
    parser = argparse.ArgumentParser(description="Voice bot with latency tracking")
    parser.add_argument(
        "--model",
        default="gpt-4.1-mini",
        choices=["gpt-4.1-mini", "gpt-4o", "gpt-4o-mini"],
        help="OpenAI model to use (default: gpt-4.1-mini)",
    )
    args = parser.parse_args()

    # -- VAD with tuned params --
    vad_analyzer = SileroVADAnalyzer(
        params=VADParams(
            threshold=0.6,
            min_volume=0.8,
        )
    )

    # -- Transport --
    transport = LocalAudioTransport(
        LocalAudioTransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_enabled=True,
            vad_analyzer=vad_analyzer,
        )
    )

    # -- Services --
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))

    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=args.model,
    )

    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
    )

    # -- Latency tracker --
    latency_tracker = LatencyTracker()

    # -- Context --
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. Keep responses under 2 sentences. "
                "Your output will be spoken aloud, so avoid special characters, "
                "bullet points, or emojis. Be conversational and concise."
            ),
        },
    ]

    context = LLMContext(messages)
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=vad_analyzer,
        ),
    )

    # -- Pipeline with latency tracking --
    # The latency tracker sits AFTER TTS to capture TTSStartedFrame (ControlFrame
    # flows downstream from TTS). UserStoppedSpeakingFrame is a SystemFrame, so
    # it reaches all processors regardless of position in the pipeline.
    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            user_aggregator,
            llm,
            tts,
            latency_tracker,         # Tracks UserStoppedSpeaking + TTSStarted
            transport.output(),
            assistant_aggregator,
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
    )

    # Greet the user
    async def greet():
        await asyncio.sleep(1)
        await task.queue_frames(
            [TTSSpeakFrame(
                f"Latency tracker ready, using {args.model}. Go ahead and speak!"
            )]
        )

    runner = PipelineRunner(handle_sigint=True)

    logger.info(f"Starting voice bot with latency tracking (model: {args.model})...")
    logger.info("Latency will be displayed after each exchange.")
    logger.info("Press Ctrl+C to stop.")

    await asyncio.gather(runner.run(task), greet())


if __name__ == "__main__":
    asyncio.run(main())
