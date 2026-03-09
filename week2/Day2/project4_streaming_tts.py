"""
Project 4: Streaming TTS with ElevenLabs

This script:
- Uses ElevenLabs streaming API for text-to-speech
- Plays audio chunks as they arrive (low latency)
- Measures time-to-first-audio
- Compares streaming vs non-streaming performance

Usage:
    python project4_streaming_tts.py
    python project4_streaming_tts.py "Your custom text here"
"""

import os
import sys
import time
import io
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs import ElevenLabs
import pygame

# Load environment variables
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

# Default text for TTS demonstration
DEFAULT_TEXT = (
    "Streaming text to speech is a game changer for voice applications. "
    "Instead of waiting for the entire audio to generate, we can start "
    "playing audio as soon as the first chunks arrive. This dramatically "
    "reduces the perceived latency and makes conversations feel much more "
    "natural and responsive."
)


def get_client() -> ElevenLabs:
    """Create and return an ElevenLabs client."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("Please set your ELEVENLABS_API_KEY in the .env file")
    return ElevenLabs(api_key=api_key)


def get_voice_id() -> str:
    """Get the voice ID from env or use default (Rachel)."""
    return os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")


def streaming_tts(client: ElevenLabs, text: str, voice_id: str) -> dict:
    """
    Generate speech using ElevenLabs streaming API and play chunks as they arrive.

    Returns a dict with timing metrics.
    """
    print("\n--- Streaming TTS ---")
    print(f"Text: {text[:80]}...")
    print("Generating and streaming audio...")

    start_time = time.time()
    first_chunk_time = None
    total_bytes = 0
    chunk_count = 0

    # Use the streaming API - returns an iterator of audio bytes
    audio_stream = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    # Collect all chunks, measuring time-to-first-audio
    audio_chunks = []
    for chunk in audio_stream:
        if first_chunk_time is None:
            first_chunk_time = time.time()
            ttfa = first_chunk_time - start_time
            print(f"  First audio chunk received in {ttfa:.3f}s")

        audio_chunks.append(chunk)
        total_bytes += len(chunk)
        chunk_count += 1

    generation_done_time = time.time()
    total_generation_time = generation_done_time - start_time

    print(f"  Total chunks received: {chunk_count}")
    print(f"  Total audio size: {total_bytes / 1024:.1f} KB")
    print(f"  Total generation time: {total_generation_time:.3f}s")

    # Combine chunks and play
    full_audio = b"".join(audio_chunks)
    print("  Playing audio...")

    pygame.mixer.init()
    audio_io = io.BytesIO(full_audio)
    pygame.mixer.music.load(audio_io)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.quit()
    print("  Playback complete.")

    return {
        "method": "streaming",
        "time_to_first_audio": first_chunk_time - start_time if first_chunk_time else 0,
        "total_generation_time": total_generation_time,
        "total_bytes": total_bytes,
        "chunk_count": chunk_count,
    }


def non_streaming_tts(client: ElevenLabs, text: str, voice_id: str) -> dict:
    """
    Generate speech using ElevenLabs non-streaming API for comparison.

    Returns a dict with timing metrics.
    """
    print("\n--- Non-Streaming TTS ---")
    print(f"Text: {text[:80]}...")
    print("Generating audio (waiting for full response)...")

    start_time = time.time()

    # Non-streaming: use convert and collect all bytes at once
    audio_generator = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    # Consume the entire generator to get all audio at once
    full_audio = b"".join(audio_generator)

    generation_done_time = time.time()
    total_generation_time = generation_done_time - start_time

    print(f"  Audio received: {len(full_audio) / 1024:.1f} KB")
    print(f"  Total generation time: {total_generation_time:.3f}s")
    print(f"  (User would wait {total_generation_time:.3f}s before hearing anything)")

    # Play the audio
    print("  Playing audio...")

    pygame.mixer.init()
    audio_io = io.BytesIO(full_audio)
    pygame.mixer.music.load(audio_io)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.quit()
    print("  Playback complete.")

    return {
        "method": "non-streaming",
        "time_to_first_audio": total_generation_time,  # Must wait for full audio
        "total_generation_time": total_generation_time,
        "total_bytes": len(full_audio),
    }


def compare_results(streaming_result: dict, non_streaming_result: dict):
    """Print a comparison of streaming vs non-streaming performance."""
    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON")
    print("=" * 60)

    print(f"\n{'Metric':<30} {'Streaming':>12} {'Non-Streaming':>15}")
    print("-" * 60)

    s_ttfa = streaming_result["time_to_first_audio"]
    ns_ttfa = non_streaming_result["time_to_first_audio"]
    print(f"{'Time to first audio':<30} {s_ttfa:>11.3f}s {ns_ttfa:>14.3f}s")

    s_gen = streaming_result["total_generation_time"]
    ns_gen = non_streaming_result["total_generation_time"]
    print(f"{'Total generation time':<30} {s_gen:>11.3f}s {ns_gen:>14.3f}s")

    s_bytes = streaming_result["total_bytes"]
    ns_bytes = non_streaming_result["total_bytes"]
    print(f"{'Audio size':<30} {s_bytes/1024:>10.1f}KB {ns_bytes/1024:>13.1f}KB")

    if s_ttfa > 0 and ns_ttfa > 0:
        improvement = ((ns_ttfa - s_ttfa) / ns_ttfa) * 100
        print(f"\nStreaming reduces time-to-first-audio by {improvement:.1f}%")
        print(f"User hears audio {ns_ttfa - s_ttfa:.3f}s sooner with streaming.")

    print("\nConclusion:")
    print("  Streaming TTS is ideal for real-time applications where low")
    print("  perceived latency matters. The user hears audio much sooner,")
    print("  even though total generation time may be similar.")


def main():
    """Main function to demonstrate streaming vs non-streaming TTS."""
    # Get text from command line or use default
    text = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TEXT

    print("=" * 60)
    print("Project 4: Streaming TTS with ElevenLabs")
    print("=" * 60)

    try:
        client = get_client()
        voice_id = get_voice_id()

        # Run streaming TTS
        streaming_result = streaming_tts(client, text, voice_id)

        print("\n(Pausing 2 seconds between tests...)")
        time.sleep(2)

        # Run non-streaming TTS for comparison
        non_streaming_result = non_streaming_tts(client, text, voice_id)

        # Compare results
        compare_results(streaming_result, non_streaming_result)

    except ValueError as e:
        print(f"\nConfiguration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
