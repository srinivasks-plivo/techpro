"""
Project 3: Configure Plivo SIP Trunk to LiveKit
================================================
This script demonstrates:
- Creating a LiveKit SIP inbound trunk via the API
- Setting up SIP dispatch rules for incoming calls
- Routing Plivo phone calls to LiveKit agent rooms
- Listing and managing SIP configuration

Usage:
    python project3_sip_config.py setup     # Create trunk + dispatch rule
    python project3_sip_config.py list      # List existing config
    python project3_sip_config.py cleanup   # Remove all SIP config
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from livekit import api

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)


def check_env_vars():
    """Check that all required environment variables are set."""
    required = [
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "PLIVO_PHONE_NUMBER",
    ]
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        print(f"\n{'='*60}")
        print("Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print(f"{'='*60}\n")
        sys.exit(1)


async def create_inbound_trunk(lk: api.LiveKitAPI, phone_number: str) -> str:
    """Create a LiveKit SIP inbound trunk.

    Args:
        lk: LiveKit API client.
        phone_number: The Plivo phone number (e.g., +15551234567).

    Returns:
        The trunk ID.
    """
    trunk = api.SIPInboundTrunkInfo(
        name="Plivo Inbound Trunk",
        numbers=[phone_number],
        krisp_enabled=False,
    )

    request = api.CreateSIPInboundTrunkRequest(trunk=trunk)
    result = await lk.sip.create_inbound_trunk(request)

    print(f"  Trunk created: id={result.sip_trunk_id}")
    print(f"  Name: {result.name}")
    print(f"  Numbers: {list(result.numbers)}")
    return result.sip_trunk_id


async def create_dispatch_rule(lk: api.LiveKitAPI, trunk_id: str) -> str:
    """Create a SIP dispatch rule that routes calls to the receptionist agent.

    Args:
        lk: LiveKit API client.
        trunk_id: The SIP inbound trunk ID to associate.

    Returns:
        The dispatch rule ID.
    """
    request = api.CreateSIPDispatchRuleRequest(
        name="Receptionist Dispatch Rule",
        rule=api.SIPDispatchRule(
            dispatch_rule_individual=api.SIPDispatchRuleIndividual(
                room_prefix="call-",
            ),
        ),
        trunk_ids=[trunk_id],
        hide_phone_number=False,
        room_config=api.RoomConfiguration(
            agents=[
                api.RoomAgentDispatch(
                    agent_name="receptionist-agent",
                ),
            ],
        ),
    )

    result = await lk.sip.create_dispatch_rule(request)

    print(f"  Dispatch rule created: id={result.sip_dispatch_rule_id}")
    print(f"  Name: {result.name}")
    print(f"  Room prefix: call-")
    print(f"  Agent: receptionist-agent")
    return result.sip_dispatch_rule_id


async def list_sip_config(lk: api.LiveKitAPI):
    """List all SIP inbound trunks and dispatch rules."""
    # List inbound trunks
    trunks = await lk.sip.list_inbound_trunk(api.ListSIPInboundTrunkRequest())
    print(f"\nInbound Trunks ({len(trunks.items)}):")
    if not trunks.items:
        print("  (none)")
    for trunk in trunks.items:
        print(f"  - ID: {trunk.sip_trunk_id}")
        print(f"    Name: {trunk.name}")
        print(f"    Numbers: {list(trunk.numbers)}")

    # List dispatch rules
    rules = await lk.sip.list_dispatch_rule(api.ListSIPDispatchRuleRequest())
    print(f"\nDispatch Rules ({len(rules.items)}):")
    if not rules.items:
        print("  (none)")
    for rule in rules.items:
        print(f"  - ID: {rule.sip_dispatch_rule_id}")
        print(f"    Name: {rule.name}")
        print(f"    Trunk IDs: {list(rule.trunk_ids)}")


async def cleanup_sip_config(lk: api.LiveKitAPI):
    """Remove all SIP dispatch rules and inbound trunks."""
    # Delete dispatch rules first (they reference trunks)
    rules = await lk.sip.list_dispatch_rule(api.ListSIPDispatchRuleRequest())
    for rule in rules.items:
        await lk.sip.delete_dispatch_rule(
            api.DeleteSIPDispatchRuleRequest(
                sip_dispatch_rule_id=rule.sip_dispatch_rule_id,
            )
        )
        print(f"  Deleted dispatch rule: {rule.sip_dispatch_rule_id}")

    # Delete inbound trunks
    trunks = await lk.sip.list_inbound_trunk(api.ListSIPInboundTrunkRequest())
    for trunk in trunks.items:
        await lk.sip.delete_trunk(
            api.DeleteSIPTrunkRequest(
                sip_trunk_id=trunk.sip_trunk_id,
            )
        )
        print(f"  Deleted inbound trunk: {trunk.sip_trunk_id}")


async def setup():
    """Create SIP inbound trunk and dispatch rule."""
    phone_number = os.getenv("PLIVO_PHONE_NUMBER")
    livekit_url = os.getenv("LIVEKIT_URL")

    lk = api.LiveKitAPI(url=livekit_url)
    try:
        print("\n[1/2] Creating SIP inbound trunk...")
        trunk_id = await create_inbound_trunk(lk, phone_number)

        print("\n[2/2] Creating dispatch rule...")
        rule_id = await create_dispatch_rule(lk, trunk_id)

        print(f"\n{'='*60}")
        print("SIP Configuration Complete!")
        print(f"{'='*60}")
        print(f"Trunk ID:    {trunk_id}")
        print(f"Rule ID:     {rule_id}")
        print(f"Phone:       {phone_number}")
        print(f"Agent Name:  receptionist-agent")
        print(f"Room Prefix: call-")
        print(f"\n{'='*60}")
        print("MANUAL STEPS IN PLIVO CONSOLE:")
        print(f"{'='*60}")
        print("1. Go to https://console.plivo.com/")
        print("2. Navigate to Voice > SIP Trunking")
        print("3. Create a SIP endpoint pointing to LiveKit's SIP URI")
        print(f"   (Check your LiveKit Cloud dashboard for the SIP URI)")
        print("4. Configure your phone number to forward to this SIP endpoint")
        print(f"\nAlternatively, in LiveKit Cloud dashboard:")
        print("1. Go to Settings > SIP")
        print("2. Your inbound trunk should be visible")
        print("3. Copy the SIP URI and configure it in Plivo")
        print(f"{'='*60}\n")
    finally:
        await lk.aclose()


async def list_config():
    """List existing SIP configuration."""
    lk = api.LiveKitAPI(url=os.getenv("LIVEKIT_URL"))
    try:
        await list_sip_config(lk)
    finally:
        await lk.aclose()


async def cleanup():
    """Remove all SIP configuration."""
    confirm = input("\nThis will delete ALL SIP trunks and dispatch rules. Continue? (y/N): ")
    if confirm.lower() != "y":
        print("Cancelled.")
        return

    lk = api.LiveKitAPI(url=os.getenv("LIVEKIT_URL"))
    try:
        print("\nCleaning up SIP configuration...")
        await cleanup_sip_config(lk)
        print("\nCleanup complete!")
    finally:
        await lk.aclose()


def main():
    """Main entry point with CLI subcommands."""
    print(f"\n{'='*60}")
    print("Project 3: Plivo SIP Trunk Configuration")
    print(f"{'='*60}")

    check_env_vars()

    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python project3_sip_config.py setup     # Create trunk + dispatch rule")
        print("  python project3_sip_config.py list      # List existing config")
        print("  python project3_sip_config.py cleanup   # Remove all SIP config")
        sys.exit(1)

    command = sys.argv[1]

    if command == "setup":
        asyncio.run(setup())
    elif command == "list":
        asyncio.run(list_config())
    elif command == "cleanup":
        asyncio.run(cleanup())
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: setup, list, cleanup")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
