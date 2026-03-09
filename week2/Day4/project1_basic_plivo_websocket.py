"""
Project 1: Basic Plivo WebSocket Server

A basic Flask server that:
- Has an /answer endpoint returning Plivo XML to start audio streaming
- Has a WebSocket server that logs when Plivo connects
- Logs when audio packets arrive (doesn't process them yet)

Usage:
    1. pip install -r requirements.txt
    2. python project1_basic_plivo_websocket.py
    3. In another terminal: ngrok http 5000
    4. Configure Plivo phone number Answer URL to: https://your-ngrok-url/answer (POST)
    5. Call your Plivo number and watch the logs
"""

import asyncio
import base64
import json
import os
import threading
from datetime import datetime
from pathlib import Path

import websockets
from dotenv import load_dotenv
from flask import Flask, Response, request

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

app = Flask(__name__)

# Track connection stats
stats = {
    "connections": 0,
    "audio_packets": 0,
    "start_events": 0,
    "stop_events": 0,
    "dtmf_events": 0,
}

# The ngrok URL will be set here - update after starting ngrok
NGROK_URL = os.getenv("NGROK_URL", "your-ngrok-url")
WS_PORT = 5001
HTTP_PORT = int(os.getenv("SERVER_PORT", 5000))


@app.route("/answer", methods=["GET", "POST"])
def answer():
    """Plivo hits this endpoint when someone calls your number.
    Returns XML telling Plivo to stream audio to our WebSocket server.
    """
    caller = request.values.get("From", "unknown")
    to_number = request.values.get("To", "unknown")
    call_uuid = request.values.get("CallUUID", "unknown")

    print(f"\n{'='*60}")
    print(f"INCOMING CALL")
    print(f"  From:     {caller}")
    print(f"  To:       {to_number}")
    print(f"  CallUUID: {call_uuid}")
    print(f"  Time:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # Construct the WebSocket URL
    # When using ngrok, replace the https:// with wss://
    ws_url = NGROK_URL.replace("https://", "wss://").replace("http://", "ws://")
    ws_url = f"{ws_url}/audio-stream"

    # If NGROK_URL hasn't been set, use localhost
    if "your-ngrok-url" in ws_url:
        ws_url = f"ws://localhost:{WS_PORT}/audio-stream"
        print(f"WARNING: NGROK_URL not set. Using localhost: {ws_url}")
        print("Set NGROK_URL in .env or as environment variable.")

    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Stream bidirectional="true" keepCallAlive="true" contentType="audio/x-mulaw;rate=8000">
        {ws_url}
    </Stream>
</Response>"""

    print(f"Returning XML with WebSocket URL: {ws_url}")
    return Response(xml_response, mimetype="application/xml")


@app.route("/status", methods=["GET"])
def status():
    """Health check / stats endpoint."""
    return {
        "status": "running",
        "stats": stats,
        "ws_port": WS_PORT,
        "http_port": HTTP_PORT,
    }


async def handle_websocket(websocket):
    """Handle incoming WebSocket connections from Plivo."""
    stats["connections"] += 1
    stream_id = None
    call_id = None

    print(f"\n[WebSocket] New connection from Plivo (total: {stats['connections']})")
    print(f"[WebSocket] Path: {websocket.path}")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                event = data.get("event", "unknown")

                if event == "start":
                    stats["start_events"] += 1
                    stream_id = data.get("streamId", "unknown")
                    call_id = data.get("callId", "unknown")
                    print(f"\n[Stream START]")
                    print(f"  Stream ID:    {stream_id}")
                    print(f"  Call ID:      {call_id}")
                    print(f"  Content Type: {data.get('contentType', 'unknown')}")
                    print(f"  Full event:   {json.dumps(data, indent=2)}")

                elif event == "media":
                    stats["audio_packets"] += 1
                    media = data.get("media", {})
                    payload = media.get("payload", "")
                    audio_bytes = base64.b64decode(payload) if payload else b""
                    seq = data.get("sequenceNumber", "?")

                    # Log every 50th packet to avoid spam
                    if stats["audio_packets"] % 50 == 1:
                        print(
                            f"[Audio] Packet #{seq} | "
                            f"Track: {media.get('track', '?')} | "
                            f"Chunk: {media.get('chunk', '?')} | "
                            f"Size: {len(audio_bytes)} bytes | "
                            f"Total packets: {stats['audio_packets']}"
                        )

                elif event == "stop":
                    stats["stop_events"] += 1
                    print(f"\n[Stream STOP]")
                    print(f"  Stream ID: {stream_id}")
                    print(f"  Reason:    {data.get('reason', 'unknown')}")
                    print(f"  Total audio packets received: {stats['audio_packets']}")

                elif event == "dtmf":
                    stats["dtmf_events"] += 1
                    digit = data.get("digit", "?")
                    print(f"[DTMF] Key pressed: {digit}")

                else:
                    print(f"[Unknown event] {event}: {json.dumps(data, indent=2)}")

            except json.JSONDecodeError:
                print(f"[WebSocket] Received non-JSON message: {message[:100]}")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"\n[WebSocket] Connection closed: code={e.code}, reason={e.reason}")
    except Exception as e:
        print(f"\n[WebSocket] Error: {e}")
    finally:
        print(f"[WebSocket] Connection ended. Stream ID: {stream_id}")
        print(f"[WebSocket] Session stats: {stats['audio_packets']} audio packets received")


async def start_websocket_server():
    """Start the WebSocket server."""
    server = await websockets.serve(handle_websocket, "0.0.0.0", WS_PORT)
    print(f"WebSocket server running on ws://0.0.0.0:{WS_PORT}")
    await server.wait_closed()


def run_websocket_server():
    """Run the WebSocket server in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_websocket_server())


if __name__ == "__main__":
    print("=" * 60)
    print("Project 1: Basic Plivo WebSocket Server")
    print("=" * 60)
    print(f"\nHTTP server (Flask):      http://0.0.0.0:{HTTP_PORT}")
    print(f"WebSocket server:         ws://0.0.0.0:{WS_PORT}")
    print(f"\nEndpoints:")
    print(f"  /answer  - Plivo Answer URL (returns streaming XML)")
    print(f"  /status  - Server stats")
    print(f"\nSetup steps:")
    print(f"  1. Start ngrok: ngrok http {HTTP_PORT}")
    print(f"  2. Set NGROK_URL env var or update .env")
    print(f"  3. Configure Plivo number Answer URL to: https://your-ngrok-url/answer")
    print(f"  4. Call your Plivo number!")
    print("=" * 60 + "\n")

    # Start WebSocket server in background thread
    ws_thread = threading.Thread(target=run_websocket_server, daemon=True)
    ws_thread.start()

    # Start Flask HTTP server in main thread
    app.run(host="0.0.0.0", port=HTTP_PORT, debug=False)
