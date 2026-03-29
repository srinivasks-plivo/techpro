"""
Project 4: Phone to LiveKit Agent
==================================
This script demonstrates:
- Voice agent with named agent_name for SIP dispatch routing
- Phone call -> Plivo -> SIP -> LiveKit -> Agent
- Logging SIP participant metadata (caller number, etc.)
- End-to-end phone conversation

Usage:
    python project4_phone_agent.py console    # Console testing
    python project4_phone_agent.py dev        # Dev mode (use this for testing phone calls)
    python project4_phone_agent.py start      # Production mode
"""

import logging
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

logger = logging.getLogger("phone-agent")

call_logger = CallLogger(db_path=str(Path(__file__).resolve().parent / "phone_agent_calls.db"))


class PhoneAgent(Agent):
    """A voice assistant optimized for phone calls via SIP."""

    def __init__(self, room=None) -> None:
        super().__init__(
            instructions=(
                "You are a helpful phone assistant. Keep responses brief and conversational. "
                "You are speaking on a phone call, so be natural and concise. "
                "Do not use emojis, asterisks, markdown, or special characters. "
                "Respond in 1-2 sentences unless asked for more detail."
            ),
        )
        self._call_id: int | None = None
        self._room = room

    async def on_enter(self):
        """Greet the phone caller."""
        try:
            room_name = self._room.name if self._room else "unknown"
            caller_number = "unknown"
            if self._room:
                for p in self._room.remote_participants.values():
                    logger.info(
                        f"Phone participant: identity={p.identity}, "
                        f"name={p.name}, metadata={p.metadata}"
                    )
                    if p.identity:
                        caller_number = p.identity
            self._call_id = call_logger.start_call(
                caller_number=caller_number,
                room_name=room_name,
            )
            logger.info(f"Call started: id={self._call_id}, room={room_name}, caller={caller_number}")
        except Exception as e:
            logger.error(f"ERROR in on_enter call logging: {e}", exc_info=True)

        self.session.generate_reply(
            instructions="Greet the caller and ask how you can help. Keep it brief.",
            allow_interruptions=False,
        )

    @function_tool
    async def get_current_time(self, context: RunContext) -> str:
        """Called when the caller asks what time it is.

        Returns the current date and time.
        """
        from datetime import datetime

        now = datetime.now()
        logger.info("Function called: get_current_time")
        return f"The current date and time is {now.strftime('%A, %B %d, %Y at %I:%M %p')}."


def prewarm(proc: JobProcess):
    """Pre-load the Silero VAD model during process startup."""
    proc.userdata["vad"] = silero.VAD.load()


server = AgentServer(setup_fnc=prewarm)


@server.rtc_session(agent_name="receptionist-agent")
async def entrypoint(ctx: JobContext):
    """Phone agent entrypoint. Matches the SIP dispatch rule agent_name."""
    logger.info(f"Phone call received in room: {ctx.room.name}")

    agent = PhoneAgent(room=ctx.room)

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

    # Metrics
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)
        if not agent._call_id:
            return
        m = ev.metrics
        if hasattr(m, "ttft") and m.ttft is not None:
            call_logger.add_latency_entry(
                agent._call_id, "llm_ttft", m.ttft,
                model_name=getattr(m, "model_name", ""),
            )
        if hasattr(m, "ttfb") and m.ttfb is not None:
            call_logger.add_latency_entry(
                agent._call_id, "tts_ttfb", m.ttfb,
                model_name=getattr(m, "model_name", ""),
            )

    @session.on("user_input_transcribed")
    def _on_user_transcript(ev):
        if agent._call_id and ev.transcript.strip():
            call_logger.add_transcript_entry(agent._call_id, "user", ev.transcript.strip())

    @session.on("agent_speech_committed")
    def _on_agent_speech(ev):
        if agent._call_id and ev.content.strip():
            call_logger.add_transcript_entry(agent._call_id, "assistant", ev.content.strip())

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Call ended. Usage: {summary}")
        if agent._call_id:
            call_logger.complete_call(
                agent._call_id,
                summary=f"Call completed. Usage: {summary}",
            )

    ctx.add_shutdown_callback(log_usage)

    await session.start(
        agent=agent,
        room=ctx.room,
    )


if __name__ == "__main__":
    cli.run_app(server)
