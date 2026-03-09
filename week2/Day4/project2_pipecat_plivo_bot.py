"""
Project 2: Pipecat Bot with Plivo Transport

A full Pipecat voice bot connected to Plivo phone calls:
- Uses FastAPIWebsocketTransport with PlivoFrameSerializer for audio I/O
- Pipeline: PlivoTransport -> SileroVAD -> Deepgram STT -> OpenAI GPT-4.1-mini -> ElevenLabs TTS -> PlivoTransport
- System prompt: "You are a helpful phone assistant. Keep responses brief and conversational."
- Handles Plivo audio format (mulaw, 8kHz)
- Flask endpoint for /answer returning streaming XML

Usage:
    1. pip install -r requirements.txt
    2. python project2_pipecat_plivo_bot.py
    3. In another terminal: ngrok http 8765
    4. Configure Plivo phone number Answer URL to: https://your-ngrok-url/ (GET)
    5. Call your Plivo number and have a conversation!
"""

import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request, WebSocket
from fastapi.responses import Response as FastAPIResponse
from loguru import logger

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

app = FastAPI(title="Pipecat Plivo Bot", description="Voice bot with Plivo phone integration")

SERVER_PORT = int(os.getenv("SERVER_PORT", 8765))


def get_ws_url(host: str) -> str:
    """Construct the WebSocket URL for Plivo streaming."""
    return f"wss://{host}/ws"


@app.get("/")
async def answer(
    request: Request,
    CallUUID: str = Query(None),
    From: str = Query(None),
    To: str = Query(None),
):
    """Plivo Answer URL - returns XML to start audio streaming to our WebSocket."""
    host = request.headers.get("host", "localhost")

    if From:
        logger.info(f"Incoming call: {From} -> {To}, CallUUID: {CallUUID}")

    ws_url = get_ws_url(host)

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Stream bidirectional="true" keepCallAlive="true" contentType="audio/x-mulaw;rate=8000">
        {ws_url}
    </Stream>
</Response>"""

    logger.info(f"Returning Plivo XML with WebSocket URL: {ws_url}")
    return FastAPIResponse(content=xml, media_type="application/xml")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections from Plivo audio streaming."""
    await websocket.accept()
    logger.info("Plivo WebSocket connection accepted")

    try:
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
        from pipecat.services.openai.llm import OpenAILLMService
        from pipecat.transports.websocket.fastapi import (
            FastAPIWebsocketParams,
            FastAPIWebsocketTransport,
        )

        # Parse Plivo's initial WebSocket messages to get stream/call info
        transport_type, call_data = await parse_telephony_websocket(websocket)
        logger.info(f"Detected transport: {transport_type}, call data: {call_data}")

        # Create the Plivo serializer with stream and call identifiers
        serializer = PlivoFrameSerializer(
            stream_id=call_data["stream_id"],
            call_id=call_data.get("call_id", ""),
            auth_id=os.getenv("PLIVO_AUTH_ID", ""),
            auth_token=os.getenv("PLIVO_AUTH_TOKEN", ""),
        )

        # Create the WebSocket transport with Plivo-specific settings
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

        # Conversation context with system prompt
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful phone assistant. Keep responses brief and "
                    "conversational. You are speaking on a phone call, so use natural "
                    "language without special characters, markdown, or formatting. "
                    "Be friendly but concise."
                ),
            },
        ]

        context = LLMContext(messages)
        user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
            context,
            user_params=LLMUserAggregatorParams(
                vad_analyzer=SileroVADAnalyzer(),
            ),
        )

        # Build the pipeline
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
            logger.info("Client connected - starting conversation")
            messages.append(
                {"role": "system", "content": "Greet the caller warmly and ask how you can help."}
            )
            await task.queue_frames([LLMRunFrame()])

        @transport.event_handler("on_client_disconnected")
        async def on_client_disconnected(transport, client):
            logger.info("Client disconnected - ending pipeline")
            await task.cancel()

        runner = PipelineRunner(handle_sigint=False)
        await runner.run(task)

    except Exception as e:
        logger.error(f"Error in WebSocket handler: {e}")
        try:
            await websocket.close()
        except Exception:
            pass


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Project 2: Pipecat Bot with Plivo Transport")
    logger.info("=" * 60)
    logger.info(f"Server running on http://0.0.0.0:{SERVER_PORT}")
    logger.info(f"Answer URL: http://0.0.0.0:{SERVER_PORT}/")
    logger.info(f"WebSocket:  ws://0.0.0.0:{SERVER_PORT}/ws")
    logger.info("")
    logger.info("Setup steps:")
    logger.info(f"  1. Start ngrok: ngrok http {SERVER_PORT}")
    logger.info("  2. Set Plivo Answer URL to: https://your-ngrok-url/ (GET)")
    logger.info("  3. Call your Plivo number!")
    logger.info("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
