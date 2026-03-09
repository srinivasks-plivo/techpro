"""
Project 2: LiveKit Voice Agent (Browser + Console Test)
=======================================================
This script demonstrates:
- Building a voice AI agent with LiveKit Agents SDK
- Pipeline: SileroVAD -> Deepgram STT (nova-3) -> OpenAI GPT-4.1-mini -> ElevenLabs TTS
- Testing via LiveKit Agents Playground (browser)
- Testing via console mode (local terminal)

Usage:
    python project2_voice_agent.py console    # Local terminal testing
    python project2_voice_agent.py dev        # Dev mode with hot reload
    python project2_voice_agent.py start      # Production mode
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
from livekit.plugins import silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

logger = logging.getLogger("voice-agent")


class VoiceAgent(Agent):
    """A helpful voice assistant powered by LiveKit Agents."""

    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a helpful voice assistant. Keep responses brief and conversational. "
                "Respond in 1-2 sentences unless the user asks for more detail. "
                "Do not use emojis, asterisks, markdown, or special characters in your responses. "
                "Speak naturally as if having a real conversation."
            ),
        )

    async def on_enter(self):
        """Called when the agent enters the session. Generates an initial greeting."""
        self.session.generate_reply(
            instructions="Greet the user briefly and ask how you can help.",
            allow_interruptions=False,
        )

    @function_tool
    async def get_current_time(self, context: RunContext) -> str:
        """Called when the user asks what time it is or asks about the current time.

        Returns the current date and time.
        """
        from datetime import datetime

        now = datetime.now()
        logger.info("Function called: get_current_time")
        return f"The current date and time is {now.strftime('%A, %B %d, %Y at %I:%M %p')}."

    @function_tool
    async def get_weather(self, context: RunContext, location: str) -> str:
        """Called when the user asks about the weather in a specific location.

        Args:
            location: The city or location to get weather for.

        Returns:
            A mock weather report for the location.
        """
        logger.info(f"Function called: get_weather for {location}")
        return f"It's currently 72 degrees and sunny in {location}. Perfect day to be outside!"


def prewarm(proc: JobProcess):
    """Pre-load the Silero VAD model during process startup for faster session starts."""
    proc.userdata["vad"] = silero.VAD.load()


server = AgentServer(setup_fnc=prewarm)


@server.rtc_session()
async def entrypoint(ctx: JobContext):
    """Main agent entrypoint. Called when a participant joins a room."""
    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt="deepgram/nova-3",
        llm="openai/gpt-4.1-mini",
        tts="elevenlabs",
        turn_detection=MultilingualModel(),
        allow_interruptions=True,
        min_endpointing_delay=0.5,
        max_endpointing_delay=3.0,
        preemptive_generation=True,
        resume_false_interruption=True,
        false_interruption_timeout=2.0,
    )

    # Metrics collection for latency tracking
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage summary: {summary}")

    ctx.add_shutdown_callback(log_usage)

    await session.start(
        agent=VoiceAgent(),
        room=ctx.room,
    )


if __name__ == "__main__":
    cli.run_app(server)
