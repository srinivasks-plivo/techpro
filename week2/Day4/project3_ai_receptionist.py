"""
Project 3: AI Receptionist with Intent Detection and Database Logging

A complete AI receptionist for Acme Corp:
- Greets callers and routes based on intent (sales, support, hours, location)
- Function calling for business info and department transfers
- Logs each call to Vercel Postgres (caller_number, transcript, detected_intent, duration, timestamp)
- Uses Pipecat pipeline: PlivoTransport -> SileroVAD -> Deepgram STT -> OpenAI GPT-4.1-mini -> ElevenLabs TTS -> PlivoTransport

Usage:
    1. pip install -r requirements.txt
    2. Set up Vercel Postgres and add POSTGRES_URL to .env
    3. python project3_ai_receptionist.py
    4. Start ngrok: ngrok http 8765
    5. Configure Plivo Answer URL to: https://your-ngrok-url/ (GET)
    6. Call and test different scenarios (sales, support, hours, location, unclear)
"""

import asyncio
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import asyncpg
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request, WebSocket
from fastapi.responses import Response as FastAPIResponse
from loguru import logger

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

app = FastAPI(title="AI Receptionist", description="Acme Corp AI phone receptionist")

SERVER_PORT = int(os.getenv("SERVER_PORT", 8765))

RECEPTIONIST_SYSTEM_PROMPT = """You are a friendly receptionist for Acme Corp.

When someone calls:
1. Greet them: "Hello, thank you for calling Acme Corp. How can I help you today?"
2. Listen to their request
3. If they want sales: Use the transfer_to_sales function, then say "I'll connect you to our sales team. One moment please." and end gracefully.
4. If they want support: Use the transfer_to_support function, then say "I'll connect you to support. Can you briefly describe your issue?"
5. If they ask about hours: Use the get_business_hours function and relay the information naturally.
6. If they ask about location: Use the get_location function and relay the information naturally.
7. If unclear: Say "I'm sorry, could you repeat that?"

Keep responses brief and natural. Don't be robotic. You are on a phone call so do not use special characters, markdown, or formatting. Speak naturally."""

# Function definitions for OpenAI tool calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_business_hours",
            "description": "Get the business hours for Acme Corp",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_location",
            "description": "Get the physical address and location of Acme Corp",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_to_sales",
            "description": "Transfer the caller to the sales department. Use when the caller wants to buy something, get pricing, or speak to sales.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_to_support",
            "description": "Transfer the caller to the support department. Use when the caller has a technical issue, needs help, or wants customer support.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


class CallLogger:
    """Logs call data to Vercel Postgres."""

    def __init__(self):
        self.pool = None
        self.transcript_parts = []
        self.detected_intents = []
        self.call_start_time = None
        self.caller_number = "unknown"

    async def connect(self):
        """Connect to Vercel Postgres."""
        postgres_url = os.getenv("POSTGRES_URL")
        if not postgres_url:
            logger.warning("POSTGRES_URL not set - call logging disabled")
            return False

        try:
            self.pool = await asyncpg.create_pool(postgres_url, min_size=1, max_size=3)
            await self._create_table()
            logger.info("Connected to Vercel Postgres for call logging")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Postgres: {e}")
            return False

    async def _create_table(self):
        """Create the call_logs table if it doesn't exist."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS call_logs (
                    id SERIAL PRIMARY KEY,
                    caller_number VARCHAR(50),
                    transcript TEXT,
                    detected_intent VARCHAR(100),
                    duration_seconds FLOAT,
                    timestamp TIMESTAMPTZ DEFAULT NOW()
                )
            """)

    def start_call(self, caller_number: str):
        """Mark the start of a call."""
        self.call_start_time = time.time()
        self.caller_number = caller_number or "unknown"
        self.transcript_parts = []
        self.detected_intents = []
        logger.info(f"Call started from {self.caller_number}")

    def add_transcript(self, role: str, text: str):
        """Add a transcript entry."""
        self.transcript_parts.append(f"{role}: {text}")

    def add_intent(self, intent: str):
        """Record a detected intent."""
        if intent not in self.detected_intents:
            self.detected_intents.append(intent)
            logger.info(f"Intent detected: {intent}")

    async def end_call(self):
        """Log the completed call to Postgres."""
        if not self.pool:
            logger.warning("No database connection - skipping call log")
            return

        duration = time.time() - self.call_start_time if self.call_start_time else 0
        transcript = "\n".join(self.transcript_parts)
        intent = ", ".join(self.detected_intents) if self.detected_intents else "none"

        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO call_logs (caller_number, transcript, detected_intent, duration_seconds, timestamp)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    self.caller_number,
                    transcript,
                    intent,
                    duration,
                    datetime.now(timezone.utc),
                )
            logger.info(
                f"Call logged: {self.caller_number}, duration={duration:.1f}s, intent={intent}"
            )
        except Exception as e:
            logger.error(f"Failed to log call: {e}")

    async def close(self):
        """Close database pool."""
        if self.pool:
            await self.pool.close()


@app.get("/")
async def answer(
    request: Request,
    CallUUID: str = Query(None),
    From: str = Query(None),
    To: str = Query(None),
):
    """Plivo Answer URL - returns XML to start audio streaming."""
    host = request.headers.get("host", "localhost")
    ws_url = f"wss://{host}/ws"

    if From:
        logger.info(f"Incoming call: {From} -> {To}, CallUUID: {CallUUID}")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Stream bidirectional="true" keepCallAlive="true" contentType="audio/x-mulaw;rate=8000">
        {ws_url}
    </Stream>
</Response>"""

    return FastAPIResponse(content=xml, media_type="application/xml")


@app.get("/calls")
async def get_call_logs():
    """View recent call logs from the database."""
    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        return {"error": "POSTGRES_URL not configured"}

    try:
        conn = await asyncpg.connect(postgres_url)
        rows = await conn.fetch(
            "SELECT * FROM call_logs ORDER BY timestamp DESC LIMIT 20"
        )
        await conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        return {"error": str(e)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections from Plivo audio streaming."""
    await websocket.accept()
    logger.info("Plivo WebSocket connection accepted for receptionist")

    call_logger = CallLogger()
    await call_logger.connect()

    try:
        from pipecat.adapters.schemas.function_schema import FunctionSchema
        from pipecat.adapters.schemas.tools_schema import ToolsSchema
        from pipecat.audio.vad.silero import SileroVADAnalyzer
        from pipecat.frames.frames import LLMRunFrame
        from pipecat.pipeline.pipeline import Pipeline
        from pipecat.pipeline.runner import PipelineRunner
        from pipecat.pipeline.task import PipelineParams, PipelineTask
        from pipecat.processors.aggregators.llm_context import LLMContext
        from pipecat.processors.aggregators.llm_response_universal import (
            LLMContextAggregatorPair,
            LLMUserAggregatorParams,
        )
        from pipecat.runner.utils import parse_telephony_websocket
        from pipecat.serializers.plivo import PlivoFrameSerializer
        from pipecat.services.deepgram.stt import DeepgramSTTService
        from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
        from pipecat.services.llm_service import FunctionCallParams
        from pipecat.services.openai.llm import OpenAILLMService
        from pipecat.transports.websocket.fastapi import (
            FastAPIWebsocketParams,
            FastAPIWebsocketTransport,
        )

        # Parse Plivo WebSocket connection
        transport_type, call_data = await parse_telephony_websocket(websocket)
        logger.info(f"Transport: {transport_type}, call data: {call_data}")

        # Start logging the call
        call_logger.start_call(call_data.get("from", "unknown"))

        serializer = PlivoFrameSerializer(
            stream_id=call_data["stream_id"],
            call_id=call_data.get("call_id", ""),
            auth_id=os.getenv("PLIVO_AUTH_ID", ""),
            auth_token=os.getenv("PLIVO_AUTH_TOKEN", ""),
        )

        transport = FastAPIWebsocketTransport(
            websocket=websocket,
            params=FastAPIWebsocketParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                add_wav_header=False,
                serializer=serializer,
            ),
        )

        # Initialize AI services
        llm = OpenAILLMService(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4.1-mini",
        )

        stt = DeepgramSTTService(
            api_key=os.getenv("DEEPGRAM_API_KEY"),
        )

        tts = ElevenLabsTTSService(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
            voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
        )

        # Register function handlers for intent detection
        async def handle_get_business_hours(params: FunctionCallParams):
            call_logger.add_intent("hours_inquiry")
            result = {
                "hours": "Monday to Friday, 9 AM to 5 PM Pacific time",
                "timezone": "Pacific Time (PT)",
                "weekend": "Closed on weekends",
            }
            logger.info(f"Function called: get_business_hours")
            await params.result_callback(result)

        async def handle_get_location(params: FunctionCallParams):
            call_logger.add_intent("location_inquiry")
            result = {
                "address": "123 Main Street, San Francisco, CA 94105",
                "city": "San Francisco",
                "state": "California",
            }
            logger.info(f"Function called: get_location")
            await params.result_callback(result)

        async def handle_transfer_to_sales(params: FunctionCallParams):
            call_logger.add_intent("sales_transfer")
            result = {
                "status": "transferring",
                "department": "Sales",
                "message": "Caller is being transferred to the sales team.",
            }
            logger.info(f"Function called: transfer_to_sales")
            await params.result_callback(result)

        async def handle_transfer_to_support(params: FunctionCallParams):
            call_logger.add_intent("support_transfer")
            result = {
                "status": "transferring",
                "department": "Support",
                "message": "Caller is being transferred to the support team.",
            }
            logger.info(f"Function called: transfer_to_support")
            await params.result_callback(result)

        llm.register_function("get_business_hours", handle_get_business_hours)
        llm.register_function("get_location", handle_get_location)
        llm.register_function("transfer_to_sales", handle_transfer_to_sales)
        llm.register_function("transfer_to_support", handle_transfer_to_support)

        # Define function schemas for the LLM context
        tools = ToolsSchema(
            standard_tools=[
                FunctionSchema(
                    name="get_business_hours",
                    description="Get the business hours for Acme Corp",
                    properties={},
                    required=[],
                ),
                FunctionSchema(
                    name="get_location",
                    description="Get the physical address and location of Acme Corp",
                    properties={},
                    required=[],
                ),
                FunctionSchema(
                    name="transfer_to_sales",
                    description="Transfer the caller to the sales department. Use when the caller wants to buy something, get pricing, or speak to sales.",
                    properties={},
                    required=[],
                ),
                FunctionSchema(
                    name="transfer_to_support",
                    description="Transfer the caller to the support department. Use when the caller has a technical issue, needs help, or wants customer support.",
                    properties={},
                    required=[],
                ),
            ]
        )

        messages = [
            {"role": "system", "content": RECEPTIONIST_SYSTEM_PROMPT},
        ]

        context = LLMContext(messages, tools=tools)
        user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
            context,
            user_params=LLMUserAggregatorParams(
                vad_analyzer=SileroVADAnalyzer(),
            ),
        )

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
                audio_in_sample_rate=8000,
                audio_out_sample_rate=8000,
                enable_metrics=True,
                enable_usage_metrics=True,
            ),
        )

        @transport.event_handler("on_client_connected")
        async def on_client_connected(transport, client):
            logger.info("Caller connected - greeting")
            messages.append(
                {
                    "role": "system",
                    "content": "The caller has just connected. Greet them with: Hello, thank you for calling Acme Corp. How can I help you today?",
                }
            )
            await task.queue_frames([LLMRunFrame()])

        @transport.event_handler("on_client_disconnected")
        async def on_client_disconnected(transport, client):
            logger.info("Caller disconnected - logging call")
            await call_logger.end_call()
            await task.cancel()

        runner = PipelineRunner(handle_sigint=False)
        await runner.run(task)

    except Exception as e:
        logger.error(f"Error in receptionist WebSocket handler: {e}")
        await call_logger.end_call()
        try:
            await websocket.close()
        except Exception:
            pass
    finally:
        await call_logger.close()


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Project 3: AI Receptionist for Acme Corp")
    logger.info("=" * 60)
    logger.info(f"Server running on http://0.0.0.0:{SERVER_PORT}")
    logger.info(f"Answer URL:  http://0.0.0.0:{SERVER_PORT}/")
    logger.info(f"Call Logs:   http://0.0.0.0:{SERVER_PORT}/calls")
    logger.info(f"WebSocket:   ws://0.0.0.0:{SERVER_PORT}/ws")
    logger.info("")
    logger.info("Features:")
    logger.info("  - Greets callers as Acme Corp receptionist")
    logger.info("  - Detects intent: sales, support, hours, location")
    logger.info("  - Function calling for business info")
    logger.info("  - Logs all calls to Vercel Postgres")
    logger.info("")
    logger.info("Setup:")
    logger.info(f"  1. Start ngrok: ngrok http {SERVER_PORT}")
    logger.info("  2. Set Plivo Answer URL to: https://your-ngrok-url/ (GET)")
    logger.info("  3. Call your Plivo number!")
    logger.info("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
