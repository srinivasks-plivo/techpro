"""
Project 2: Local Voice Bot (Microphone/Speaker)
================================================
A Pipecat bot that uses local audio transport (mic and speakers).

Pipeline:
    Microphone -> SileroVAD + SmartTurn -> Deepgram STT -> OpenAI GPT-4.1-mini -> ElevenLabs TTS -> Speaker

Features:
    - Uses LocalAudioTransport for mic input and speaker output
    - SileroVAD for voice activity detection with tuned params
    - SmartTurn for ML-based end-of-turn detection (waits for natural pauses)
    - Deepgram for real-time speech-to-text
    - OpenAI GPT-4.1-mini for fast LLM responses
    - ElevenLabs for high-quality text-to-speech
    - Handles interruptions (stops speaking when user talks)

Usage:
    python project2_local_voice_bot.py

Verification:
    1. Bot starts and listens via microphone
    2. Speak a question and listen for the response
    3. Try interrupting mid-response -- the bot should stop
    4. Have a 5-turn conversation
"""

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
from pipecat.turns.user_turn_strategies import UserTurnStrategies

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


async def main():
    # -- VAD with tuned params for local mic --
    # High threshold + min_volume to avoid triggering on speaker bleed / echo.
    # If using speakers (not headphones), the mic can pick up the bot's own
    # TTS output and treat it as user speech. These values help filter that out.
    vad_analyzer = SileroVADAnalyzer(
        params=VADParams(
            threshold=0.6,
            min_volume=0.8,
        )
    )

    # -- Transport: Local audio (mic + speakers) --
    transport = LocalAudioTransport(
        LocalAudioTransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_enabled=True,
            vad_analyzer=vad_analyzer,
        )
    )

    # -- STT: Deepgram --
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))

    # -- LLM: OpenAI GPT-4.1-mini --
    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4.1-mini",
    )

    # -- TTS: ElevenLabs --
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

    # SmartTurn uses an ML model to detect when the user is truly done speaking,
    # not just pausing to think. This prevents the bot from cutting you off.
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=vad_analyzer,
            user_turn_strategies=UserTurnStrategies(),
        ),
    )

    # -- Build the pipeline --
    pipeline = Pipeline(
        [
            transport.input(),       # Microphone audio input
            stt,                     # Speech-to-Text (Deepgram)
            user_aggregator,         # Collects user transcription into LLM context
            llm,                     # LLM processing (OpenAI GPT-4.1-mini)
            tts,                     # Text-to-Speech (ElevenLabs)
            transport.output(),      # Speaker audio output
            assistant_aggregator,    # Collects assistant response into LLM context
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
            allow_interruptions=True,
        ),
    )

    # Greet the user when the bot starts
    async def greet():
        await asyncio.sleep(1)
        await task.queue_frames(
            [TTSSpeakFrame("Hello! I'm your voice assistant. How can I help you today?")]
        )

    runner = PipelineRunner(handle_sigint=True)

    logger.info("Starting local voice bot... Speak into your microphone!")
    logger.info("Using SmartTurn for natural turn detection.")
    logger.info("Press Ctrl+C to stop.")

    await asyncio.gather(runner.run(task), greet())


if __name__ == "__main__":
    asyncio.run(main())
