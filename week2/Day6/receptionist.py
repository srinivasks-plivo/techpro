"""
Day 6: Pipecat AI Receptionist — Railway Deployment
====================================================
Deployed version of the improved AI receptionist (Day 4 Project 4).
No PyTorch needed — Pipecat uses onnxruntime for Silero VAD.

Usage (local):  python receptionist.py
Usage (deploy): railway up
"""

import os
import time
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI, Query, Request, WebSocket
from fastapi.responses import Response as FastAPIResponse
from loguru import logger
from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.adapters.schemas.tools_schema import ToolsSchema
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import Frame, TextFrame, TranscriptionFrame, TTSSpeakFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
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

app = FastAPI(title="Acme Corp AI Receptionist")

# Railway sets PORT automatically; fallback to SERVER_PORT or 8765
SERVER_PORT = int(os.getenv("PORT", os.getenv("SERVER_PORT", 8765)))

# Store caller info from /answer so WebSocket handler can access it
_pending_calls = {}


class TranscriptProcessor(FrameProcessor):
    """Captures user (STT) and bot (TTS) text for logging."""

    def __init__(self, call_logger):
        super().__init__()
        self._call_logger = call_logger

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        if isinstance(frame, TranscriptionFrame) and frame.text.strip():
            self._call_logger.add_transcript("user", frame.text.strip())
        elif isinstance(frame, TextFrame) and frame.text.strip():
            self._call_logger.add_transcript("assistant", frame.text.strip())
        await self.push_frame(frame, direction)

# ---------------------------------------------------------------------------
# WARM-START: Pre-initialize expensive resources at server startup
# ---------------------------------------------------------------------------
logger.info("Warm-start: Loading Silero VAD model...")
_warm_vad = SileroVADAnalyzer(
    params=VADParams(threshold=0.5, min_volume=0.6)
)
logger.info("Warm-start: Silero VAD model ready")

_warm_llm = OpenAILLMService(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4.1-mini",
)
_warm_stt = DeepgramSTTService(
    api_key=os.getenv("DEEPGRAM_API_KEY"),
)
_warm_tts = ElevenLabsTTSService(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
    voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
)
logger.info("Warm-start: AI services (LLM, STT, TTS) pre-initialized")

IMPROVED_SYSTEM_PROMPT = """You are a friendly, natural-sounding receptionist for Plivo Inc. You are speaking on a phone call.

ABOUT PLIVO:
Plivo is a cloud communications platform that enables businesses to make and receive voice calls and SMS messages globally.
Products include: Voice API, SMS API, SIP Trunking, Phone Number Management, and Contact Center solutions.
Plivo serves over 50,000 businesses worldwide including IBM, Netflix, and MercadoLibre.

IMPORTANT CONVERSATION RULES:
- Keep responses brief and conversational - one to two sentences max.
- Do NOT use special characters, markdown, bullet points, or formatting. Speak naturally as a human would on the phone.
- Remember what the caller has already asked about during this call. If they ask a follow-up, connect it to the previous topic.
- After helping with a request, always ask: "Is there anything else I can help you with?"
- When the caller says goodbye, they're done, or "that's all", respond with: "Thank you for calling Plivo. Have a great day. Goodbye!"
- If you cannot understand what the caller said, say: "I'm sorry, I'm having a bit of trouble hearing you. Could you please repeat that?"

HANDLING REQUESTS:
1. Greet new callers: "Hello, thank you for calling Plivo. How can I help you today?"
2. Sales inquiries: Use transfer_to_sales function. Say "I'll connect you to our sales team. One moment please."
3. Support inquiries: Use transfer_to_support function. Say "I'll connect you to our support team. Can you briefly describe your issue?"
4. Hours questions: Use get_business_hours function and relay naturally.
5. Location questions: Use get_location function and relay naturally.
6. Product questions: Plivo offers Voice API for programmable calls, SMS API for messaging, SIP Trunking for connecting existing phone systems, and Contact Center for building customer support solutions. For pricing details, offer to connect them to sales.
7. Unclear requests: "I'm sorry, could you repeat that?"

CONTEXT AWARENESS:
- If someone asks about products then asks "how much does it cost?", offer to connect them to sales for pricing details.
- If someone asks about hours then asks "what about weekends?", answer about weekend support hours.
- If someone asks about location then asks "do you have other offices?", mention the other offices.
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
            import asyncpg
            self.pool = await asyncpg.create_pool(postgres_url, min_size=1, max_size=3)
            await self._create_table()
            logger.info("Connected to Vercel Postgres")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Postgres: {e}")
            return False

    async def _create_table(self):
        async with self.pool.acquire() as conn:
            # Add new columns if table already exists, or create fresh
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS call_logs (
                    id SERIAL PRIMARY KEY,
                    caller_number VARCHAR(50),
                    to_number VARCHAR(50) DEFAULT 'unknown',
                    call_uuid VARCHAR(100) DEFAULT '',
                    transcript TEXT,
                    detected_intent VARCHAR(100),
                    duration_seconds FLOAT,
                    timestamp TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            # Add columns if they don't exist (for existing tables)
            for col, typ in [("to_number", "VARCHAR(50) DEFAULT 'unknown'"), ("call_uuid", "VARCHAR(100) DEFAULT ''")]:
                try:
                    await conn.execute(f"ALTER TABLE call_logs ADD COLUMN IF NOT EXISTS {col} {typ}")
                except Exception:
                    pass

    def start_call(self, caller_number: str, to_number: str = "unknown", call_uuid: str = "unknown"):
        self.call_start_time = time.time()
        self.caller_number = caller_number or "unknown"
        self.to_number = to_number or "unknown"
        self.call_uuid = call_uuid or "unknown"
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
                    INSERT INTO call_logs (caller_number, to_number, call_uuid, transcript, detected_intent, duration_seconds, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    self.caller_number,
                    self.to_number,
                    self.call_uuid,
                    transcript,
                    intent,
                    duration,
                    datetime.now(timezone.utc),
                )
            logger.info(f"Call logged: {self.caller_number} -> {self.to_number}, {duration:.1f}s, intent={intent}")
        except Exception as e:
            logger.error(f"Failed to log call: {e}")

    async def close(self):
        if self.pool:
            await self.pool.close()


@app.get("/health")
async def health():
    """Health check endpoint for Railway monitoring."""
    return {"status": "healthy", "service": "acme-receptionist"}


@app.api_route("/answer", methods=["GET", "POST"])
@app.api_route("/", methods=["GET", "POST"])
async def answer(request: Request):
    """Plivo Answer URL — handles both GET (query params) and POST (form body)."""
    # Extract params from query string OR form body
    if request.method == "POST":
        form = await request.form()
        params = dict(form)
    else:
        params = dict(request.query_params)

    caller = params.get("From", "unknown")
    to_number = params.get("To", "unknown")
    call_uuid = params.get("CallUUID", "unknown")

    host = request.headers.get("host", "localhost")
    ws_url = f"wss://{host}/ws"

    logger.info(f"Incoming call: {caller} -> {to_number}, CallUUID: {call_uuid}")

    # Store caller info so WebSocket handler can access it
    _pending_calls[call_uuid] = {"from": caller, "to": to_number, "call_uuid": call_uuid}
    # Also store by caller number as fallback
    _pending_calls[caller] = {"from": caller, "to": to_number, "call_uuid": call_uuid}

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
        import asyncpg
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
        # Parse Plivo WebSocket
        transport_type, call_data = await parse_telephony_websocket(websocket)
        logger.info(f"Transport: {transport_type}, data: {call_data}")

        # Get caller info from /answer endpoint
        # Try matching by call_id, stream_id, or grab the most recent pending call
        call_id = call_data.get("call_id", "")
        stream_id = call_data.get("stream_id", "")
        caller_info = (
            _pending_calls.pop(call_id, None)
            or _pending_calls.pop(stream_id, None)
            or (list(_pending_calls.values())[-1] if _pending_calls else {})
        )
        # Clean up any remaining entries for this call
        if caller_info:
            for k, v in list(_pending_calls.items()):
                if v.get("call_uuid") == caller_info.get("call_uuid"):
                    _pending_calls.pop(k, None)

        logger.info(f"call_data keys: {call_data}")
        logger.info(f"caller_info resolved: {caller_info}")

        caller_number = caller_info.get("from", call_data.get("from", "unknown"))
        to_number = caller_info.get("to", "unknown")
        call_uuid = caller_info.get("call_uuid", call_id)

        call_logger.start_call(caller_number, to_number, call_uuid)
        logger.info(f"Call started: {caller_number} -> {to_number}, UUID: {call_uuid}")

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
                vad_enabled=True,
                vad_analyzer=_warm_vad,
            ),
        )

        # Fresh service instances per call (shared instances break after first
        # call because ElevenLabs/Deepgram WebSocket connections get closed)
        llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4.1-mini")
        stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
        tts = ElevenLabsTTSService(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
            voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
        )

        # Transcript capture processor
        transcript_processor = TranscriptProcessor(call_logger)

        # Register function handlers
        async def handle_get_business_hours(params: FunctionCallParams):
            call_logger.add_intent("hours_inquiry")
            logger.info("Function: get_business_hours")
            await params.result_callback({
                "weekday_hours": "Monday to Friday, 9 AM to 6 PM Pacific Time",
                "support_hours": "24/7 support available for premium plans",
                "weekend_hours": "Limited support on weekends for enterprise customers",
                "timezone": "Pacific Time (PT), with global support teams",
            })

        async def handle_get_location(params: FunctionCallParams):
            call_logger.add_intent("location_inquiry")
            logger.info("Function: get_location")
            await params.result_callback({
                "headquarters": "340 S Lemon Ave, Suite 1116, Walnut, CA 91789, USA",
                "austin_office": "Austin, Texas",
                "bangalore_office": "Bangalore, India",
                "website": "plivo.com",
                "contact_email": "support@plivo.com",
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
                    description="Get business hours for Plivo Inc including weekday, weekend, and support hours.",
                    properties={},
                    required=[],
                ),
                FunctionSchema(
                    name="get_location",
                    description="Get office locations, address, and contact info for Plivo Inc.",
                    properties={},
                    required=[],
                ),
                FunctionSchema(
                    name="transfer_to_sales",
                    description="Transfer caller to Plivo sales team for pricing, demos, or product inquiries.",
                    properties={},
                    required=[],
                ),
                FunctionSchema(
                    name="transfer_to_support",
                    description="Transfer caller to Plivo support team for technical issues or account help.",
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
                vad_analyzer=_warm_vad,
            ),
        )

        pipeline = Pipeline(
            [
                transport.input(),
                stt,
                transcript_processor,
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
            logger.info("Caller connected - sending instant greeting")
            # Send greeting directly to TTS (skips LLM round trip = ~1-2s faster)
            await task.queue_frames([
                TTSSpeakFrame("Hello, thank you for calling Plivo. How can I help you today?")
            ])

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
    logger.info("Acme Corp AI Receptionist (Pipecat + Plivo)")
    logger.info("=" * 60)
    logger.info(f"Server:  http://0.0.0.0:{SERVER_PORT}")
    logger.info(f"Health:  http://0.0.0.0:{SERVER_PORT}/health")
    logger.info(f"Answer:  http://0.0.0.0:{SERVER_PORT}/answer")
    logger.info(f"Calls:   http://0.0.0.0:{SERVER_PORT}/calls")
    logger.info(f"WS:      ws://0.0.0.0:{SERVER_PORT}/ws")
    logger.info("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
