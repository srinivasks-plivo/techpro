"""
Project 2: Real-Time Transcription with Deepgram

This script:
- Captures microphone audio using sounddevice
- Streams audio to Deepgram's real-time WebSocket API
- Prints words as they are recognized in real time
- Press Ctrl+C to stop

Usage:
    python project2_realtime_transcription.py
"""

import os
import sys
import json
import asyncio
import signal
from pathlib import Path

import numpy as np
import sounddevice as sd
import websockets
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
BLOCKSIZE = 4096  # frames per buffer

# Deepgram real-time WebSocket endpoint
DEEPGRAM_WS_URL = "wss://api.deepgram.com/v1/listen"


async def run_transcription():
    """Main coroutine that streams mic audio to Deepgram and prints results."""
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key or api_key == "your_deepgram_key_here":
        print("Error: Please set your DEEPGRAM_API_KEY in the .env file")
        sys.exit(1)

    # Build WebSocket URL with query parameters
    params = (
        f"?encoding=linear16"
        f"&sample_rate={SAMPLE_RATE}"
        f"&channels={CHANNELS}"
        f"&model=nova-2"
        f"&language=en"
        f"&punctuate=true"
        f"&interim_results=true"
    )
    url = DEEPGRAM_WS_URL + params

    headers = {
        "Authorization": f"Token {api_key}",
    }

    print("=" * 50)
    print("REAL-TIME TRANSCRIPTION (Deepgram)")
    print("=" * 50)
    print("Connecting to Deepgram...")

    async with websockets.connect(url, additional_headers=headers) as ws:
        print("Connected! Listening on microphone...")
        print("Speak into your microphone. Press Ctrl+C to stop.\n")

        # Shared state
        stop_event = asyncio.Event()

        async def send_audio():
            """Capture mic audio and send to Deepgram over WebSocket."""
            loop = asyncio.get_event_loop()
            audio_queue = asyncio.Queue()

            def audio_callback(indata, frames, time_info, status):
                if status:
                    print(f"[Audio status: {status}]", file=sys.stderr)
                # Convert float32 to int16 PCM bytes
                audio_data = (indata[:, 0] * 32767).astype(np.int16).tobytes()
                loop.call_soon_threadsafe(audio_queue.put_nowait, audio_data)

            stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                blocksize=BLOCKSIZE,
                dtype="float32",
                callback=audio_callback,
            )

            with stream:
                while not stop_event.is_set():
                    try:
                        data = await asyncio.wait_for(audio_queue.get(), timeout=0.5)
                        await ws.send(data)
                    except asyncio.TimeoutError:
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        break

            # Send close message to Deepgram
            try:
                await ws.send(json.dumps({"type": "CloseStream"}))
            except Exception:
                pass

        async def receive_transcripts():
            """Receive and print transcription results from Deepgram."""
            last_line_len = 0
            try:
                async for message in ws:
                    result = json.loads(message)

                    # Check if this is a transcript result
                    if result.get("type") != "Results":
                        continue

                    channel = result.get("channel", {})
                    alternatives = channel.get("alternatives", [])
                    if not alternatives:
                        continue

                    transcript = alternatives[0].get("transcript", "")
                    if not transcript:
                        continue

                    is_final = result.get("is_final", False)

                    if is_final:
                        # Clear interim line and print final on its own line
                        sys.stdout.write("\r" + " " * last_line_len + "\r")
                        print(f"  {transcript}")
                        last_line_len = 0
                    else:
                        # Overwrite interim results in place
                        line = f"  ... {transcript}"
                        sys.stdout.write("\r" + " " * last_line_len + "\r")
                        sys.stdout.write(line)
                        sys.stdout.flush()
                        last_line_len = len(line)

            except websockets.exceptions.ConnectionClosed:
                pass

        # Run sender and receiver concurrently
        sender = asyncio.create_task(send_audio())
        receiver = asyncio.create_task(receive_transcripts())

        # Wait for Ctrl+C
        loop = asyncio.get_event_loop()
        stop_future = loop.create_future()

        def on_signal():
            stop_event.set()
            if not stop_future.done():
                stop_future.set_result(True)

        loop.add_signal_handler(signal.SIGINT, on_signal)

        await stop_future

        # Clean up
        sender.cancel()
        receiver.cancel()
        try:
            await sender
        except asyncio.CancelledError:
            pass
        try:
            await receiver
        except asyncio.CancelledError:
            pass

        print("\n\nTranscription stopped.")


def main():
    """Entry point."""
    try:
        asyncio.run(run_transcription())
    except KeyboardInterrupt:
        print("\nTranscription stopped.")


if __name__ == "__main__":
    main()
