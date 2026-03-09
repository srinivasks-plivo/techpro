"""
Project 3: Add SmartTurn for Better Turn Detection
===================================================
Enhances the voice bot with SmartTurn semantic turn detection.

SmartTurn goes beyond simple silence-based VAD:
    - Uses ML model to detect when user is truly done speaking
    - Distinguishes "thinking pauses" from "done speaking"
    - Reduces false interruptions for more natural conversation

Pipeline:
    Microphone -> SileroVAD + SmartTurnV3 -> Deepgram STT -> OpenAI GPT-4.1-mini
    -> ElevenLabs TTS -> Speaker

The key difference from Project 2:
    - Project 2 uses only SileroVAD (silence-based detection)
    - Project 3 uses UserTurnStrategies with SmartTurnV3 (semantic detection)

Usage:
    # With SmartTurn (default):
    python project3_smart_turn_bot.py

    # Without SmartTurn (for comparison):
    python project3_smart_turn_bot.py --no-smart-turn

Verification:
    1. Run without SmartTurn, note behavior with pauses
    2. Run with SmartTurn, compare -- it should wait for complete thoughts
    3. Test: "I want to order... hmm... maybe a pizza" -- SmartTurn waits
    4. SmartTurn should feel more natural than VAD alone
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import TTSSpeakFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


async def main():
    parser = argparse.ArgumentParser(description="Voice bot with optional SmartTurn")
    parser.add_argument(
        "--no-smart-turn",
        action="store_true",
        help="Disable SmartTurn (use only VAD silence detection)",
    )
    args = parser.parse_args()

    use_smart_turn = not args.no_smart_turn

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
        model="gpt-4.1-mini",
    )

    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
    )

    # -- Conversation context --
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

    # -- Configure turn detection --
    if use_smart_turn:
        # SmartTurn uses ML-based end-of-turn detection.
        # UserTurnStrategies defaults to LocalSmartTurnAnalyzerV3 for stop detection,
        # combined with VAD + Transcription for start detection.
        from pipecat.turns.user_turn_strategies import UserTurnStrategies

        logger.info("SmartTurn ENABLED -- using ML-based turn detection")
        user_params = LLMUserAggregatorParams(
            vad_analyzer=vad_analyzer,
            user_turn_strategies=UserTurnStrategies(),  # defaults include SmartTurnV3
        )
    else:
        # VAD-only: relies on silence duration to detect end of speech.
        # This can cut users off during thinking pauses.
        logger.info("SmartTurn DISABLED -- using VAD silence detection only")
        user_params = LLMUserAggregatorParams(
            vad_analyzer=vad_analyzer,
        )

    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=user_params,
    )

    # -- Pipeline --
    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            user_aggregator,
            llm,
            tts,
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
        mode = "SmartTurn" if use_smart_turn else "VAD-only"
        await task.queue_frames(
            [TTSSpeakFrame(f"Hello! Voice bot with {mode} turn detection is ready. Go ahead and speak!")]
        )

    runner = PipelineRunner(handle_sigint=True)

    mode_str = "SmartTurn (semantic)" if use_smart_turn else "VAD-only (silence)"
    logger.info(f"Starting voice bot with {mode_str} turn detection...")
    logger.info("Press Ctrl+C to stop.")

    await asyncio.gather(runner.run(task), greet())


if __name__ == "__main__":
    asyncio.run(main())
