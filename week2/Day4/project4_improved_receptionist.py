"""
Project 4: Improved AI Receptionist with Better Conversation Quality

Enhancements over Project 3:
- Better interruption handling: Stops TTS immediately when caller speaks
- Conversation context: Remembers what was discussed earlier in the call
- Graceful ending: "Is there anything else I can help you with?" -> "Thank you for calling. Goodbye!"
- Error recovery: If STT fails, says "I'm having trouble hearing you, could you repeat that?"

Usage:
    1. pip install -r requirements.txt
    2. Set up Vercel Postgres and add POSTGRES_URL to .env
    3. python project4_improved_receptionist.py
    4. Start ngrok: ngrok http 8765
    5. Configure Plivo Answer URL to: https://your-ngrok-url/ (GET)
    6. Test: interruptions, context follow-ups, graceful ending, error recovery
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

app = FastAPI(
    title="Improved AI Receptionist",
    description="Acme Corp receptionist with enhanced conversation quality",
)

SERVER_PORT = int(os.getenv("SERVER_PORT", 8765))

IMPROVED_SYSTEM_PROMPT = """You are a friendly, natural-sounding receptionist for Acme Corp. You are speaking on a phone call.

IMPORTANT CONVERSATION RULES:
- Keep responses brief and conversational - one to two sentences max.
- Do NOT use special characters, markdown, bullet points, or formatting. Speak naturally as a human would on the phone.
- Remember what the caller has already asked about during this call. If they ask a follow-up like "what about weekends?" after asking about hours, connect it to the previous topic.
- After helping with a request, always ask: "Is there anything else I can help you with?"
- When the caller says goodbye, they're done, or "that's all", respond with: "Thank you for calling Acme Corp. Have a great day. Goodbye!"
- If you cannot understand what the caller said, say: "I'm sorry, I'm having a bit of trouble hearing you. Could you please repeat that?"

HANDLING REQUESTS:
1. Greet new callers: "Hello, thank you for calling Acme Corp. How can I help you today?"
2. Sales inquiries: Use transfer_to_sales function. Say "I'll connect you to our sales team. One moment please."
3. Support inquiries: Use transfer_to_support function. Say "I'll connect you to support. Can you briefly describe your issue?"
4. Hours questions: Use get_business_hours function and relay naturally.
5. Location questions: Use get_location function and relay naturally.
6. Unclear requests: "I'm sorry, could you repeat that?"

CONTEXT AWARENESS:
- If someone asks about hours then asks "what about weekends?", you should answer about weekend hours.
- If someone asks about location then asks "how do I get there?", give directions context.
- Track the conversation flow and provide contextually relevant responses."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_business_hours",
            "description": "Get the business hours for Acme Corp. Returns weekday and weekend hours.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_location",
            "description": "Get the physical address, location, and directions info for Acme Corp",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_to_sales",
            "description": "Transfer the caller to the sales department",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_to_support",
            "description": "Transfer the caller to the support department",
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
        postgres_url = os.getenv("POSTGRES_URL")
        if not postgres_url:
            logger.warning("POSTGRES_URL not set - call logging disabled")
            return False
        try:
            self.pool = await asyncpg.create_pool(postgres_url, min_size=1, max_size=3)
            await self._create_table()
            logger.info("Connected to Vercel Postgres")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Postgres: {e}")
            return False

    async def _create_table(self):
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
        self.call_start_time = time.time()
        self.caller_number = caller_number or "unknown"
        self.transcript_parts = []
        self.detected_intents = []

    def add_transcript(self, role: str, text: str):
        self.transcript_parts.append(f"{role}: {text}")

    def add_intent(self, intent: str):
        if intent not in self.detected_intents:
            self.detected_intents.append(intent)

    async def end_call(self):
        if not self.pool:
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
            logger.info(f"Call logged: {self.caller_number}, {duration:.1f}s, intent={intent}")
        except Exception as e:
            logger.error(f"Failed to log call: {e}")

    async def close(self):
        if self.pool:
            await self.pool.close()


@app.get("/")
async def answer(
    request: Request,
    CallUUID: str = Query(None),
    From: str = Query(None),
    To: str = Query(None),
):
    """Plivo Answer URL."""
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
    """View recent call logs."""
    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        return {"error": "POSTGRES_URL not configured"}
    try:
        conn = await asyncpg.connect(postgres_url)
        rows = await conn.fetch("SELECT * FROM call_logs ORDER BY timestamp DESC LIMIT 20")
        await conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        return {"error": str(e)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections with improved conversation quality."""
    await websocket.accept()
    logger.info("Plivo WebSocket accepted - improved receptionist")

    call_logger = CallLogger()
    await call_logger.connect()

    try:
        from pipecat.adapters.schemas.function_schema import FunctionSchema
        from pipecat.adapters.schemas.tools_schema import ToolsSchema
        from pipecat.audio.vad.silero import SileroVADAnalyzer
        from pipecat.audio.vad.vad_analyzer import VADParams
        from pipecat.frames.frames import (
            LLMRunFrame,
            UserStartedSpeakingFrame,
            UserStoppedSpeakingFrame,
        )
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

        # Parse Plivo WebSocket
        transport_type, call_data = await parse_telephony_websocket(websocket)
        logger.info(f"Transport: {transport_type}, data: {call_data}")

        call_logger.start_call(call_data.get("from", "unknown"))

        serializer = PlivoFrameSerializer(
            stream_id=call_data["stream_id"],
            call_id=call_data.get("call_id", ""),
            auth_id=os.getenv("PLIVO_AUTH_ID", ""),
            auth_token=os.getenv("PLIVO_AUTH_TOKEN", ""),
        )

        # Configure VAD with parameters tuned for phone audio quality
        vad_analyzer = SileroVADAnalyzer(
            params=VADParams(
                threshold=0.5,
                min_volume=0.6,
            )
        )

        transport = FastAPIWebsocketTransport(
            websocket=websocket,
            params=FastAPIWebsocketParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                add_wav_header=False,
                serializer=serializer,
                vad_enabled=True,
                vad_analyzer=vad_analyzer,
            ),
        )

        # Initialize services
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

        # Register function handlers
        async def handle_get_business_hours(params: FunctionCallParams):
            call_logger.add_intent("hours_inquiry")
            logger.info("Function: get_business_hours")
            await params.result_callback({
                "weekday_hours": "Monday to Friday, 9 AM to 5 PM Pacific time",
                "weekend_hours": "Closed on Saturday and Sunday",
                "holidays": "Closed on major US holidays",
                "timezone": "Pacific Time (PT)",
            })

        async def handle_get_location(params: FunctionCallParams):
            call_logger.add_intent("location_inquiry")
            logger.info("Function: get_location")
            await params.result_callback({
                "address": "123 Main Street, San Francisco, CA 94105",
                "cross_streets": "Near the corner of Main and Market",
                "parking": "Street parking available, paid garage next door",
                "public_transit": "Two blocks from Montgomery BART station",
            })

        async def handle_transfer_to_sales(params: FunctionCallParams):
            call_logger.add_intent("sales_transfer")
            logger.info("Function: transfer_to_sales")
            await params.result_callback({
                "status": "transferring",
                "department": "Sales",
            })

        async def handle_transfer_to_support(params: FunctionCallParams):
            call_logger.add_intent("support_transfer")
            logger.info("Function: transfer_to_support")
            await params.result_callback({
                "status": "transferring",
                "department": "Support",
            })

        llm.register_function("get_business_hours", handle_get_business_hours)
        llm.register_function("get_location", handle_get_location)
        llm.register_function("transfer_to_sales", handle_transfer_to_sales)
        llm.register_function("transfer_to_support", handle_transfer_to_support)

        # Define tools schema
        tools = ToolsSchema(
            standard_tools=[
                FunctionSchema(
                    name="get_business_hours",
                    description="Get business hours for Acme Corp including weekday, weekend, and holiday hours.",
                    properties={},
                    required=[],
                ),
                FunctionSchema(
                    name="get_location",
                    description="Get the physical address, directions, parking, and transit info for Acme Corp.",
                    properties={},
                    required=[],
                ),
                FunctionSchema(
                    name="transfer_to_sales",
                    description="Transfer the caller to the sales department.",
                    properties={},
                    required=[],
                ),
                FunctionSchema(
                    name="transfer_to_support",
                    description="Transfer the caller to the support department.",
                    properties={},
                    required=[],
                ),
            ]
        )

        messages = [
            {"role": "system", "content": IMPROVED_SYSTEM_PROMPT},
        ]

        context = LLMContext(messages, tools=tools)
        user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
            context,
            user_params=LLMUserAggregatorParams(
                vad_analyzer=vad_analyzer,
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
                allow_interruptions=True,
            ),
        )

        @transport.event_handler("on_client_connected")
        async def on_client_connected(transport, client):
            logger.info("Caller connected - sending greeting")
            messages.append(
                {
                    "role": "system",
                    "content": "The caller just connected. Greet them warmly: Hello, thank you for calling Acme Corp. How can I help you today?",
                }
            )
            await task.queue_frames([LLMRunFrame()])

        @transport.event_handler("on_client_disconnected")
        async def on_client_disconnected(transport, client):
            logger.info("Caller disconnected")
            await call_logger.end_call()
            await task.cancel()

        runner = PipelineRunner(handle_sigint=False)
        await runner.run(task)

    except Exception as e:
        logger.error(f"Error in improved receptionist: {e}")
        await call_logger.end_call()
        try:
            await websocket.close()
        except Exception:
            pass
    finally:
        await call_logger.close()


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Project 4: Improved AI Receptionist")
    logger.info("=" * 60)
    logger.info(f"Server: http://0.0.0.0:{SERVER_PORT}")
    logger.info(f"Answer URL: http://0.0.0.0:{SERVER_PORT}/")
    logger.info(f"Call Logs:  http://0.0.0.0:{SERVER_PORT}/calls")
    logger.info(f"WebSocket:  ws://0.0.0.0:{SERVER_PORT}/ws")
    logger.info("")
    logger.info("Improvements over Project 3:")
    logger.info("  - Interruption handling (allow_interruptions=True)")
    logger.info("  - Conversation context memory (follow-up questions work)")
    logger.info("  - Graceful ending ('Thank you for calling... Goodbye!')")
    logger.info("  - Error recovery ('I'm having trouble hearing you...')")
    logger.info("  - Tuned VAD for phone audio quality")
    logger.info("")
    logger.info("Test scenarios:")
    logger.info("  1. Interrupt: Start speaking while bot is talking")
    logger.info("  2. Context: Ask about hours, then 'what about weekends?'")
    logger.info("  3. Ending: Say 'that's all, thanks'")
    logger.info("  4. Error: Make noise or mumble")
    logger.info("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
