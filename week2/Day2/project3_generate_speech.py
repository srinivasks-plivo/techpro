"""
Project 3: Generate Speech with ElevenLabs

This script:
- Takes text input from the command line
- Sends it to the ElevenLabs Text-to-Speech API
- Saves the audio as an MP3 file
- Auto-plays the generated audio

Usage:
    python project3_generate_speech.py "Hello, welcome to Speech AI!"
    python project3_generate_speech.py   # (prompts for text interactively)
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

# ElevenLabs API settings
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel

# Output directory
OUTPUT_DIR = Path(__file__).parent / "output"


def generate_speech(text: str, output_path: str = None) -> str:
    """
    Generate speech from text using the ElevenLabs API.

    Args:
        text: The text to convert to speech.
        output_path: Optional path for the output MP3 file.

    Returns:
        Path to the saved MP3 file.
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key or api_key == "your_elevenlabs_key_here":
        raise ValueError("Please set your ELEVENLABS_API_KEY in the .env file")

    voice_id = os.getenv("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)
    url = f"{ELEVENLABS_API_URL}/{voice_id}"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }

    print(f"Generating speech for: \"{text[:80]}{'...' if len(text) > 80 else ''}\"")
    print(f"Voice ID: {voice_id}")

    response = httpx.post(url, headers=headers, json=payload, timeout=60.0)

    if response.status_code != 200:
        raise Exception(
            f"ElevenLabs API error: {response.status_code} - {response.text}"
        )

    # Determine output path
    if output_path is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = str(OUTPUT_DIR / f"speech_{timestamp}.mp3")

    with open(output_path, "wb") as f:
        f.write(response.content)

    print(f"Audio saved to: {output_path}")
    return output_path


def play_audio(file_path: str):
    """
    Play an MP3 file using pygame.

    Args:
        file_path: Path to the MP3 file.
    """
    try:
        import pygame

        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        print("Playing audio... (press Ctrl+C to skip)")
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.quit()
    except ImportError:
        print("pygame not installed. Skipping playback.")
        print(f"You can play the file manually: {file_path}")
    except KeyboardInterrupt:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        print("\nPlayback stopped.")
    except Exception as e:
        print(f"Playback error: {e}")
        print(f"You can play the file manually: {file_path}")


def main():
    """Main function."""
    # Get text from command line args or interactive input
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        print("Enter text to convert to speech (press Enter when done):")
        text = input("> ").strip()
        if not text:
            print("No text provided. Exiting.")
            sys.exit(1)

    print()
    print("=" * 50)
    print("TEXT-TO-SPEECH (ElevenLabs)")
    print("=" * 50)

    try:
        # Generate speech
        output_path = generate_speech(text)

        # Play the audio
        print()
        play_audio(output_path)

        print("\nDone!")

    except ValueError as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
