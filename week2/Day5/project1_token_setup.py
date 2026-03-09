"""
Project 1: LiveKit Token Generation & Connection Verification
=============================================================
This script demonstrates:
- Generating LiveKit access tokens using the livekit-api SDK
- Verifying connection to LiveKit Cloud
- Understanding rooms, participants, and permissions

Usage:
    python project1_token_setup.py
"""

import os
import sys
import asyncio
import datetime
from pathlib import Path
from dotenv import load_dotenv
from livekit import api

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

PYTHON = sys.executable


def check_env_vars():
    """Check that all required LiveKit environment variables are set."""
    required = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET"]
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        print(f"\n{'='*60}")
        print("Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease set them in your .env file.")
        print(f"{'='*60}\n")
        sys.exit(1)
    print("All LiveKit environment variables are set.")


def generate_token(room_name: str, participant_name: str, duration_hours: int = 24) -> str:
    """Generate a LiveKit access token for a room.

    Args:
        room_name: Name of the LiveKit room to join.
        participant_name: Identity of the participant.
        duration_hours: Token validity in hours (default: 24).

    Returns:
        JWT token string.
    """
    token = (
        api.AccessToken()
        .with_identity(participant_name)
        .with_name(participant_name)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
            )
        )
        .with_ttl(datetime.timedelta(hours=duration_hours))
    )
    return token.to_jwt()


async def verify_connection():
    """Verify connection to LiveKit Cloud by listing rooms.

    Returns:
        True if connection succeeds, False otherwise.
    """
    livekit_api = api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL"),
    )
    try:
        rooms = await livekit_api.room.list_rooms(api.ListRoomsRequest())
        print(f"Connection verified! Found {len(rooms.rooms)} existing room(s).")
        if rooms.rooms:
            for room in rooms.rooms:
                print(f"  - {room.name} ({room.num_participants} participants)")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False
    finally:
        await livekit_api.aclose()


def main():
    """Main entry point."""
    print(f"\n{'='*60}")
    print("Project 1: LiveKit Token Generation & Connection Test")
    print(f"{'='*60}\n")

    # Step 1: Check environment variables
    print("[1/3] Checking environment variables...")
    check_env_vars()

    # Step 2: Verify connection
    print("\n[2/3] Verifying connection to LiveKit Cloud...")
    connected = asyncio.run(verify_connection())
    if not connected:
        print("\nFailed to connect. Check your LIVEKIT_URL, API_KEY, and API_SECRET.")
        sys.exit(1)

    # Step 3: Generate a test token
    print("\n[3/3] Generating test access token...")
    room_name = "test-room"
    participant_name = "test-user"
    token = generate_token(room_name, participant_name)

    print(f"\n{'='*60}")
    print("Token generated successfully!")
    print(f"{'='*60}")
    print(f"Room:        {room_name}")
    print(f"Participant: {participant_name}")
    print(f"Token:       {token[:50]}...")
    print(f"\nFull token (copy this):\n{token}")
    print(f"\n{'='*60}")
    print("Next Steps:")
    print("1. Open the LiveKit Agents Playground:")
    print("   https://agents-playground.livekit.io/")
    print("2. Connect to your LiveKit project")
    print("3. Start project2_voice_agent.py to test with the agent")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
