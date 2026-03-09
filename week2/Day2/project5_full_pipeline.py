"""
Project 5: Full Voice AI Pipeline (STT -> LLM -> TTS)

This script:
- Records 5 seconds of audio from the microphone
- Transcribes the recording with Deepgram (Speech-to-Text)
- Sends the transcript to OpenAI for a response (LLM)
- Generates speech from the response with ElevenLabs (Text-to-Speech)
- Plays the audio response
- Measures end-to-end latency for each stage and total

Usage:
    python project5_full_pipeline.py
"""

import os
import sys
import time
import io
import wave
import tempfile
from pathlib import Path

import numpy as np
import sounddevice as sd
from dotenv import load_dotenv
import httpx
from openai import OpenAI
from elevenlabs import ElevenLabs
import pygame

# Load environment variables
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
RECORD_SECONDS = 5
DTYPE = "int16"


def check_api_keys():
    """Verify all required API keys are set."""
    keys = {
        "DEEPGRAM_API_KEY": os.getenv("DEEPGRAM_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY"),
    }

    missing = []
    for name, value in keys.items():
        if not value or value.startswith("your_"):
            missing.append(name)

    if missing:
        raise ValueError(
            f"Missing API keys in .env file: {', '.join(missing)}\n"
            "Please set all required keys before running the pipeline."
        )

    return keys


def record_audio() -> np.ndarray:
    """
    Record audio from the microphone for RECORD_SECONDS.

    Returns:
        numpy array of recorded audio samples
    """
    print(f"\nRecording {RECORD_SECONDS} seconds of audio...")
    print("  Speak now!")

    audio_data = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE,
    )
    sd.wait()

    print("  Recording complete.")
    return audio_data


def audio_to_wav_bytes(audio_data: np.ndarray) -> bytes:
    """Convert numpy audio array to WAV format bytes."""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit = 2 bytes
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_data.tobytes())
    return buffer.getvalue()


def transcribe_with_deepgram(wav_bytes: bytes, api_key: str) -> str:
    """
    Transcribe audio using Deepgram's pre-recorded API.

    Args:
        wav_bytes: WAV format audio bytes
        api_key: Deepgram API key

    Returns:
        Transcribed text
    """
    print("\n[STT] Transcribing with Deepgram...")

    start_time = time.time()

    response = httpx.post(
        "https://api.deepgram.com/v1/listen",
        params={
            "model": "nova-2",
            "language": "en",
            "punctuate": "true",
        },
        headers={
            "Authorization": f"Token {api_key}",
            "Content-Type": "audio/wav",
        },
        content=wav_bytes,
        timeout=30.0,
    )

    elapsed = time.time() - start_time

    if response.status_code != 200:
        raise Exception(f"Deepgram error: {response.status_code} - {response.text}")

    result = response.json()
    transcript = (
        result.get("results", {})
        .get("channels", [{}])[0]
        .get("alternatives", [{}])[0]
        .get("transcript", "")
    )

    print(f"  Transcript: \"{transcript}\"")
    print(f"  STT Latency: {elapsed:.3f}s")

    return transcript, elapsed


def get_llm_response(transcript: str, api_key: str) -> str:
    """
    Get a conversational response from OpenAI.

    Args:
        transcript: User's transcribed speech
        api_key: OpenAI API key

    Returns:
        LLM response text
    """
    print("\n[LLM] Getting response from OpenAI...")

    start_time = time.time()

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful voice assistant. Keep your responses "
                    "concise and conversational, ideally 1-3 sentences. "
                    "Respond naturally as if speaking to someone."
                ),
            },
            {"role": "user", "content": transcript},
        ],
        max_tokens=150,
        temperature=0.7,
    )

    elapsed = time.time() - start_time

    reply = response.choices[0].message.content.strip()
    print(f"  Response: \"{reply}\"")
    print(f"  LLM Latency: {elapsed:.3f}s")

    return reply, elapsed


def generate_and_play_speech(text: str, api_key: str, voice_id: str) -> float:
    """
    Generate speech with ElevenLabs streaming and play it.

    Args:
        text: Text to convert to speech
        api_key: ElevenLabs API key
        voice_id: ElevenLabs voice ID

    Returns:
        TTS latency in seconds
    """
    print("\n[TTS] Generating speech with ElevenLabs...")

    start_time = time.time()

    client = ElevenLabs(api_key=api_key)

    # Use streaming for lower latency
    audio_stream = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    first_chunk_time = None
    audio_chunks = []

    for chunk in audio_stream:
        if first_chunk_time is None:
            first_chunk_time = time.time()
        audio_chunks.append(chunk)

    generation_elapsed = time.time() - start_time
    ttfa = (first_chunk_time - start_time) if first_chunk_time else generation_elapsed

    full_audio = b"".join(audio_chunks)
    print(f"  Audio generated: {len(full_audio) / 1024:.1f} KB")
    print(f"  Time to first audio: {ttfa:.3f}s")
    print(f"  TTS Generation Latency: {generation_elapsed:.3f}s")

    # Play the audio
    print("  Playing response...")
    pygame.mixer.init()
    audio_io = io.BytesIO(full_audio)
    pygame.mixer.music.load(audio_io)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.quit()
    print("  Playback complete.")

    return generation_elapsed


def main():
    """Run the full voice AI pipeline."""
    print("=" * 60)
    print("Project 5: Full Voice AI Pipeline")
    print("  STT (Deepgram) -> LLM (OpenAI) -> TTS (ElevenLabs)")
    print("=" * 60)

    try:
        # Check all API keys
        keys = check_api_keys()
        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

        # Stage 1: Record audio from microphone
        pipeline_start = time.time()
        audio_data = record_audio()
        wav_bytes = audio_to_wav_bytes(audio_data)
        record_time = time.time() - pipeline_start

        # Stage 2: Speech-to-Text with Deepgram
        transcript, stt_latency = transcribe_with_deepgram(
            wav_bytes, keys["DEEPGRAM_API_KEY"]
        )

        if not transcript:
            print("\nNo speech detected. Please try again and speak clearly.")
            sys.exit(1)

        # Stage 3: LLM response from OpenAI
        reply, llm_latency = get_llm_response(transcript, keys["OPENAI_API_KEY"])

        # Stage 4: Text-to-Speech with ElevenLabs
        tts_latency = generate_and_play_speech(
            reply, keys["ELEVENLABS_API_KEY"], voice_id
        )

        # Calculate and display end-to-end metrics
        total_pipeline_time = time.time() - pipeline_start
        processing_latency = stt_latency + llm_latency + tts_latency

        print("\n" + "=" * 60)
        print("END-TO-END LATENCY BREAKDOWN")
        print("=" * 60)
        print(f"  Recording:          {record_time:.3f}s (fixed {RECORD_SECONDS}s)")
        print(f"  STT (Deepgram):     {stt_latency:.3f}s")
        print(f"  LLM (OpenAI):       {llm_latency:.3f}s")
        print(f"  TTS (ElevenLabs):   {tts_latency:.3f}s")
        print(f"  ---------------------------------")
        print(f"  Processing latency: {processing_latency:.3f}s (STT + LLM + TTS)")
        print(f"  Total pipeline:     {total_pipeline_time:.3f}s (including recording)")
        print()
        print("Note: Processing latency is the time from end-of-recording")
        print("to start-of-playback. This is the delay a user would perceive")
        print("between finishing speaking and hearing the AI response.")

    except ValueError as e:
        print(f"\nConfiguration Error: {e}")
        sys.exit(1)
    except sd.PortAudioError as e:
        print(f"\nMicrophone Error: {e}")
        print("Make sure a microphone is connected and accessible.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
