"""
Project 5: AI Receptionist on LiveKit
======================================
This script demonstrates:
- Full-featured AI receptionist with greeting
- Intent detection using function calling (@function_tool)
- Business information functions (hours, location, transfers)
- Call logging to SQLite database
- Conversation context within calls
- Graceful call ending

Usage:
    python project5_receptionist.py console    # Console testing
    python project5_receptionist.py dev        # Dev mode with hot reload
    python project5_receptionist.py start      # Production mode
"""

import logging
import os
from pathlib import Path
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    cli,
    metrics,
)
from livekit.agents.llm import function_tool
from livekit.plugins import silero, openai, elevenlabs
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from call_logger import CallLogger

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

logger = logging.getLogger("receptionist")

call_logger = CallLogger(db_path=str(Path(__file__).resolve().parent / "receptionist_calls.db"))

RECEPTIONIST_INSTRUCTIONS = """You are a friendly and professional receptionist for Acme Corp.

When someone calls:
1. Greet them warmly: "Hello, thank you for calling Acme Corp. How can I help you today?"
2. Listen carefully to their request.
3. Use the available tools to help them:
   - If they ask about business hours, use get_business_hours()
   - If they ask about location or address, use get_location()
   - If they want to speak with sales or ask about products/pricing, use transfer_to_sales()
   - If they need technical support or have an issue, use transfer_to_support()
4. If their request is unclear, politely ask them to repeat or clarify.
5. After helping them, ask: "Is there anything else I can help you with?"
6. End calls gracefully: "Thank you for calling Acme Corp. Have a great day!"

Important rules:
- Keep responses brief and natural. Do not be robotic.
- Do not use emojis, asterisks, markdown, or special characters.
- Speak conversationally as if on a real phone call.
- Remember what was discussed earlier in the conversation for context."""


class ReceptionistAgent(Agent):
    """AI Receptionist for Acme Corp with intent detection and call logging."""

    def __init__(self, room=None) -> None:
        super().__init__(instructions=RECEPTIONIST_INSTRUCTIONS)
        self._call_id: int | None = None
        self._room = room

    async def on_enter(self):
        """Called when the agent enters the session. Starts call logging and greeting."""
        try:
            room_name = self._room.name if self._room else "unknown"

            # Try to extract caller info from room participants
            caller_number = "unknown"
            if self._room:
                for p in self._room.remote_participants.values():
                    if p.identity:
                        caller_number = p.identity
                        break

            self._call_id = call_logger.start_call(
                caller_number=caller_number,
                room_name=room_name,
            )
            logger.info(f"Call started: id={self._call_id}, room={room_name}, caller={caller_number}")
        except Exception as e:
            logger.error(f"ERROR in on_enter call logging: {e}", exc_info=True)

        self.session.generate_reply(
            instructions="Greet the caller warmly as a receptionist for Acme Corp.",
            allow_interruptions=False,
        )

    @function_tool
    async def get_business_hours(self, context: RunContext) -> str:
        """Called when the caller asks about business hours, opening times, or when Acme Corp is open.

        Returns the current business hours for Acme Corp.
        """
        logger.info("Function called: get_business_hours")
        if self._call_id:
            call_logger.add_detected_intent(self._call_id, "hours_inquiry")
        return (
            "Acme Corp is open Monday to Friday, 9 AM to 5 PM Pacific Time. "
            "We are closed on weekends and major holidays."
        )

    @function_tool
    async def get_location(self, context: RunContext) -> str:
        """Called when the caller asks about the company location, address, or how to find Acme Corp.

        Returns the office location for Acme Corp.
        """
        logger.info("Function called: get_location")
        if self._call_id:
            call_logger.add_detected_intent(self._call_id, "location_inquiry")
        return (
            "Acme Corp is located at 123 Main Street, San Francisco, California 94105. "
            "We are in the downtown financial district, near the Montgomery BART station."
        )

    @function_tool
    async def transfer_to_sales(self, context: RunContext) -> str:
        """Called when the caller wants to speak with the sales team, asks about products, pricing, or wants to make a purchase.

        Initiates a transfer to the sales department.
        """
        logger.info("Function called: transfer_to_sales")
        if self._call_id:
            call_logger.add_detected_intent(self._call_id, "sales_transfer")
        return (
            "Connecting the caller to the sales team now. "
            "Tell them: I'll connect you to our sales team. One moment please."
        )

    @function_tool
    async def transfer_to_support(self, context: RunContext) -> str:
        """Called when the caller needs technical support, has an issue, complaint, or needs help with a product.

        Initiates a transfer to the support department.
        """
        logger.info("Function called: transfer_to_support")
        if self._call_id:
            call_logger.add_detected_intent(self._call_id, "support_transfer")
        return (
            "Connecting the caller to the support team now. "
            "Tell them: I'll connect you to our support team. Can you briefly describe your issue while I connect you?"
        )


def prewarm(proc: JobProcess):
    """Pre-load the Silero VAD model during process startup."""
    proc.userdata["vad"] = silero.VAD.load()


server = AgentServer(setup_fnc=prewarm)


@server.rtc_session(agent_name="receptionist-agent")
async def entrypoint(ctx: JobContext):
    """Main receptionist entrypoint. Called when a phone call creates a room."""
    agent = ReceptionistAgent(room=ctx.room)

    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt="deepgram/nova-3",
        llm=openai.LLM(
            model="gpt-4.1-nano",
            temperature=0.7,
        ),
        tts=elevenlabs.TTS(
            voice_id="EXAVITQu4vr4xnSDxMaL",  # Sarah - natural, warm female voice
            model="eleven_multilingual_v2",
            encoding="pcm_24000",
            language="en",
        ),
        turn_detection=MultilingualModel(),
        allow_interruptions=True,
        min_endpointing_delay=0.1,
        max_endpointing_delay=0.4,
        preemptive_generation=True,
        resume_false_interruption=True,
        false_interruption_timeout=0.3,
    )

    # Metrics collection
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)
        if not agent._call_id:
            return
        m = ev.metrics
        # Log LLM time-to-first-token
        if hasattr(m, "ttft") and m.ttft is not None:
            call_logger.add_latency_entry(
                agent._call_id, "llm_ttft", m.ttft,
                model_name=getattr(m, "model_name", ""),
            )
        # Log TTS time-to-first-byte
        if hasattr(m, "ttfb") and m.ttfb is not None:
            call_logger.add_latency_entry(
                agent._call_id, "tts_ttfb", m.ttfb,
                model_name=getattr(m, "model_name", ""),
            )

    @session.on("user_input_transcribed")
    def _on_user_transcript(ev):
        if agent._call_id and ev.transcript.strip():
            call_logger.add_transcript_entry(agent._call_id, "user", ev.transcript.strip())
            logger.info(f"Logged user transcript: {ev.transcript.strip()}")

    @session.on("agent_speech_committed")
    def _on_agent_speech(ev):
        if agent._call_id and ev.content.strip():
            call_logger.add_transcript_entry(agent._call_id, "assistant", ev.content.strip())
            logger.info(f"Logged agent transcript: {ev.content.strip()}")

    async def on_shutdown():
        """Complete call logging on session end."""
        summary = usage_collector.get_summary()
        logger.info(f"Usage summary: {summary}")

        if agent._call_id:
            call_logger.complete_call(
                agent._call_id,
                summary=f"Call completed. Usage: {summary}",
            )
            call = call_logger.get_call(agent._call_id)
            if call:
                logger.info(
                    f"Call {agent._call_id} summary: "
                    f"duration={call['duration_seconds']:.1f}s, "
                    f"intents={call['detected_intents']}"
                )

    ctx.add_shutdown_callback(on_shutdown)

    await session.start(
        agent=agent,
        room=ctx.room,
    )


if __name__ == "__main__":
    cli.run_app(server)
