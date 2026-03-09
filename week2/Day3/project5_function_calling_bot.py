"""
Project 5: Add Function Calling to Voice Bot
==============================================
Adds tool/function calling to the Pipecat voice bot.

Functions:
    - get_current_time: Returns the current date and time
    - tell_joke: Returns a random joke
    - lookup_order: Looks up a mock order status by order number

The LLM decides when to call functions based on the user's voice query.
Function results are incorporated into the response and spoken naturally.

Pipeline:
    Microphone -> SileroVAD -> Deepgram STT -> User Aggregator
    -> OpenAI GPT-4.1-mini (with tools) -> ElevenLabs TTS -> Speaker
    -> Assistant Aggregator

Usage:
    python project5_function_calling_bot.py

Verification:
    1. Ask "What time is it?" -- verify time function is called
    2. Ask "Tell me a joke" -- verify joke is told
    3. Ask "What's the status of order 12345?" -- verify lookup works
    4. Ask a general question -- verify no function is called
    5. Function results are spoken naturally
"""

import asyncio
import os
import random
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.adapters.schemas.tools_schema import ToolsSchema
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
from pipecat.services.llm_service import FunctionCallParams
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

# ============================================================
# Function implementations (called by the LLM)
# ============================================================

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "Why was the JavaScript developer sad? Because he didn't Node how to Express himself.",
    "What do you call a bear with no teeth? A gummy bear.",
    "Why don't scientists trust atoms? Because they make up everything.",
    "What did the ocean say to the beach? Nothing, it just waved.",
    "Why did the scarecrow win an award? He was outstanding in his field.",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "What do you call a fake noodle? An impasta.",
]

MOCK_ORDERS = {
    "12345": {"status": "Shipped", "item": "Wireless Headphones", "delivery": "February 18, 2026"},
    "67890": {"status": "Processing", "item": "Laptop Stand", "delivery": "February 22, 2026"},
    "11111": {"status": "Delivered", "item": "USB-C Cable Pack", "delivery": "February 14, 2026"},
    "99999": {"status": "Cancelled", "item": "Phone Case", "delivery": "N/A"},
}


async def handle_get_current_time(params: FunctionCallParams):
    """Return the current date and time."""
    now = datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%A, %B %d, %Y")
    result = {"time": time_str, "date": date_str}
    logger.info(f"FUNCTION CALL: get_current_time -> {result}")
    await params.result_callback(result)


async def handle_tell_joke(params: FunctionCallParams):
    """Return a random joke."""
    joke = random.choice(JOKES)
    result = {"joke": joke}
    logger.info(f"FUNCTION CALL: tell_joke -> {result}")
    await params.result_callback(result)


async def handle_lookup_order(params: FunctionCallParams):
    """Look up an order by order number."""
    order_number = params.arguments.get("order_number", "unknown")
    order_info = MOCK_ORDERS.get(order_number)

    if order_info:
        result = {
            "order_number": order_number,
            "status": order_info["status"],
            "item": order_info["item"],
            "expected_delivery": order_info["delivery"],
        }
    else:
        result = {
            "order_number": order_number,
            "status": "Not Found",
            "message": f"No order found with number {order_number}",
        }

    logger.info(f"FUNCTION CALL: lookup_order({order_number}) -> {result}")
    await params.result_callback(result)


# ============================================================
# Function schemas (describe functions to the LLM)
# ============================================================

time_function = FunctionSchema(
    name="get_current_time",
    description="Get the current date and time. Call this when the user asks what time it is or what today's date is.",
    properties={},
    required=[],
)

joke_function = FunctionSchema(
    name="tell_joke",
    description="Tell a random joke. Call this when the user asks for a joke or wants to hear something funny.",
    properties={},
    required=[],
)

order_function = FunctionSchema(
    name="lookup_order",
    description="Look up the status of an order by its order number. Call this when the user asks about an order status or tracking.",
    properties={
        "order_number": {
            "type": "string",
            "description": "The order number to look up, e.g. '12345'",
        },
    },
    required=["order_number"],
)

tools = ToolsSchema(standard_tools=[time_function, joke_function, order_function])


async def main():
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

    # Register function handlers with the LLM
    llm.register_function("get_current_time", handle_get_current_time)
    llm.register_function("tell_joke", handle_tell_joke)
    llm.register_function("lookup_order", handle_lookup_order)

    # Optionally say something while functions are being called
    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
    )

    @llm.event_handler("on_function_calls_started")
    async def on_function_calls_started(service, function_calls):
        logger.info(f"Function calls started: {[fc.function_name for fc in function_calls]}")

    # -- Context with tools --
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful voice assistant with access to tools. "
                "Keep responses under 2 sentences. "
                "Your output will be spoken aloud, so avoid special characters, "
                "bullet points, or emojis. Be conversational and natural. "
                "When you use a tool, incorporate the result naturally into your response. "
                "Available tools: get_current_time, tell_joke, lookup_order. "
                "Only use tools when relevant to the user's question."
            ),
        },
    ]

    context = LLMContext(messages, tools)
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=vad_analyzer,
        ),
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
        await task.queue_frames(
            [TTSSpeakFrame(
                "Hello! I'm your assistant with function calling. "
                "You can ask me the time, request a joke, or check an order status. "
                "Try saying: What time is it?"
            )]
        )

    runner = PipelineRunner(handle_sigint=True)

    logger.info("Starting voice bot with function calling...")
    logger.info("Available functions: get_current_time, tell_joke, lookup_order")
    logger.info("Press Ctrl+C to stop.")

    await asyncio.gather(runner.run(task), greet())


if __name__ == "__main__":
    asyncio.run(main())
