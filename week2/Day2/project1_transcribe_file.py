
"""
Project 1: Transcribe Audio File with Deepgram

This script:
- Takes an audio file path as input (WAV or MP3)
- Sends to Deepgram's pre-recorded API
- Returns the transcript with timestamps
- Saves transcript to a text file

Usage:
    python project1_transcribe_file.py <audio_file_path>

Example:
    python project1_transcribe_file.py sample.wav
"""

import os
import sys
import httpx
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

# Deepgram API endpoint
DEEPGRAM_URL = "https://api.deepgram.com/v1/listen"


def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribe an audio file using Deepgram's pre-recorded API.

    Args:
        audio_path: Path to the audio file (WAV or MP3)

    Returns:
        Dictionary containing transcript and metadata
    """
    # Get API key
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key or api_key == "your_deepgram_key_here":
        raise ValueError("Please set your DEEPGRAM_API_KEY in the .env file")

    # Read the audio file
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    with open(audio_path, "rb") as audio_file:
        buffer_data = audio_file.read()

    # Determine content type based on file extension
    ext = audio_path.suffix.lower()
    content_types = {
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".flac": "audio/flac",
        ".ogg": "audio/ogg",
    }
    content_type = content_types.get(ext, "audio/wav")

    # Configure transcription options
    params = {
        "model": "nova-2",       # Best accuracy model
        "language": "en",        # English
        "punctuate": "true",     # Add punctuation
        "utterances": "true",    # Get utterance-level timestamps
    }

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": content_type,
    }

    print(f"Transcribing: {audio_path.name}")
    print("Sending to Deepgram...")

    # Send to Deepgram using httpx
    response = httpx.post(
        DEEPGRAM_URL,
        params=params,
        headers=headers,
        content=buffer_data,
        timeout=60.0,
    )

    if response.status_code != 200:
        raise Exception(f"Deepgram API error: {response.status_code} - {response.text}")

    return response.json()


def format_transcript(response: dict) -> str:
    """
    Format the Deepgram response into a readable transcript with timestamps.

    Args:
        response: Deepgram API response dictionary

    Returns:
        Formatted transcript string
    """
    output_lines = []

    # Get the results
    results = response.get("results", {})
    channels = results.get("channels", [])
    metadata = response.get("metadata", {})

    # Add header
    output_lines.append("=" * 60)
    output_lines.append("TRANSCRIPT")
    output_lines.append("=" * 60)
    output_lines.append("")

    # Full transcript
    if channels and channels[0].get("alternatives"):
        full_transcript = channels[0]["alternatives"][0].get("transcript", "")
        output_lines.append("FULL TRANSCRIPT:")
        output_lines.append("-" * 40)
        output_lines.append(full_transcript)
        output_lines.append("")

    # Timestamps per word
    output_lines.append("WORD TIMESTAMPS:")
    output_lines.append("-" * 40)

    if channels and channels[0].get("alternatives"):
        words = channels[0]["alternatives"][0].get("words", [])
        for word in words:
            start = word.get("start", 0)
            end = word.get("end", 0)
            text = word.get("word", "")
            timestamp = f"[{start:.2f}s - {end:.2f}s]"
            output_lines.append(f"{timestamp} {text}")

    output_lines.append("")

    # Metadata
    output_lines.append("METADATA:")
    output_lines.append("-" * 40)
    if metadata:
        duration = metadata.get("duration", 0)
        channels_count = metadata.get("channels", 1)
        output_lines.append(f"Duration: {duration:.2f} seconds")
        output_lines.append(f"Channels: {channels_count}")

    return "\n".join(output_lines)


def save_transcript(transcript: str, audio_path: str) -> str:
    """
    Save the transcript to a text file.

    Args:
        transcript: Formatted transcript string
        audio_path: Original audio file path (used for naming)

    Returns:
        Path to the saved transcript file
    """
    audio_path = Path(audio_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = audio_path.parent / f"{audio_path.stem}_transcript_{timestamp}.txt"

    with open(output_path, "w") as f:
        f.write(transcript)

    return str(output_path)


def main():
    """Main function to run the transcription."""
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python project1_transcribe_file.py <audio_file_path>")
        print("")
        print("Example:")
        print("  python project1_transcribe_file.py sample.wav")
        print("  python project1_transcribe_file.py recording.mp3")
        sys.exit(1)

    audio_path = sys.argv[1]

    try:
        # Transcribe the audio
        response = transcribe_audio(audio_path)

        # Format the transcript
        transcript = format_transcript(response)

        # Print to console
        print("")
        print(transcript)

        # Save to file
        output_path = save_transcript(transcript, audio_path)
        print("")
        print(f"Transcript saved to: {output_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Transcription Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
