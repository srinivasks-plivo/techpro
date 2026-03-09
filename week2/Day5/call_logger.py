"""
Call Logger: SQLite Database for Call Logging
=============================================
This module provides:
- SQLite database initialization
- Call logging (start, update, complete)
- Call retrieval and summary
- Easy swap to PostgreSQL later by changing the connection

Database schema:
    calls(id, caller_number, room_name, start_time, end_time,
          duration_seconds, transcript, detected_intents, summary, status)
"""

import json
import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("call-logger")


class CallLogger:
    """SQLite-backed call logger for tracking voice AI conversations."""

    def __init__(self, db_path: str = "calls.db"):
        """Initialize the call logger.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Get a new database connection (thread-safe)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self):
        """Create the calls table if it doesn't exist."""
        conn = self._get_conn()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    caller_number TEXT DEFAULT 'unknown',
                    room_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration_seconds REAL,
                    transcript TEXT DEFAULT '[]',
                    detected_intents TEXT DEFAULT '[]',
                    latency_logs TEXT DEFAULT '[]',
                    summary TEXT DEFAULT '',
                    status TEXT DEFAULT 'active'
                )
            """)
            conn.commit()
            # Migrate: add latency_logs column if missing
            columns = [row[1] for row in conn.execute("PRAGMA table_info(calls)").fetchall()]
            if "latency_logs" not in columns:
                conn.execute("ALTER TABLE calls ADD COLUMN latency_logs TEXT DEFAULT '[]'")
                conn.commit()
                logger.info("Migrated: added latency_logs column")
            logger.info(f"Database initialized at {self.db_path}")
        finally:
            conn.close()

    def start_call(self, caller_number: str, room_name: str) -> int:
        """Log the start of a new call.

        Args:
            caller_number: Phone number or identity of the caller.
            room_name: LiveKit room name.

        Returns:
            The call ID.
        """
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "INSERT INTO calls (caller_number, room_name, start_time) VALUES (?, ?, ?)",
                (caller_number, room_name, datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()
            call_id = cursor.lastrowid
            logger.info(f"Call started: id={call_id}, room={room_name}, caller={caller_number}")
            return call_id
        finally:
            conn.close()

    def add_transcript_entry(self, call_id: int, role: str, text: str):
        """Append a transcript entry to the call.

        Args:
            call_id: The call ID.
            role: Either 'user' or 'assistant'.
            text: The transcribed text.
        """
        conn = self._get_conn()
        try:
            row = conn.execute("SELECT transcript FROM calls WHERE id = ?", (call_id,)).fetchone()
            if not row:
                logger.warning(f"Call {call_id} not found for transcript update")
                return
            transcript = json.loads(row["transcript"])
            transcript.append({
                "role": role,
                "text": text,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            conn.execute(
                "UPDATE calls SET transcript = ? WHERE id = ?",
                (json.dumps(transcript), call_id),
            )
            conn.commit()
        finally:
            conn.close()

    def add_detected_intent(self, call_id: int, intent: str):
        """Record a detected intent for the call.

        Args:
            call_id: The call ID.
            intent: The detected intent (e.g., 'sales_transfer', 'hours_inquiry').
        """
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT detected_intents FROM calls WHERE id = ?", (call_id,)
            ).fetchone()
            if not row:
                logger.warning(f"Call {call_id} not found for intent update")
                return
            intents = json.loads(row["detected_intents"])
            intents.append(intent)
            conn.execute(
                "UPDATE calls SET detected_intents = ? WHERE id = ?",
                (json.dumps(intents), call_id),
            )
            conn.commit()
            logger.info(f"Call {call_id}: detected intent '{intent}'")
        finally:
            conn.close()

    def add_latency_entry(self, call_id: int, metric_type: str, latency_seconds: float, model_name: str = ""):
        """Record a latency measurement for the call.

        Args:
            call_id: The call ID.
            metric_type: Type of metric (e.g., 'llm_ttft', 'tts_ttfb', 'total_response').
            latency_seconds: Latency in seconds.
            model_name: Name of the model that produced this metric.
        """
        HIGH_LATENCY_THRESHOLD = 1.2
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT latency_logs FROM calls WHERE id = ?", (call_id,)
            ).fetchone()
            if not row:
                logger.warning(f"Call {call_id} not found for latency update")
                return
            logs = json.loads(row["latency_logs"])
            entry = {
                "type": metric_type,
                "latency_s": round(latency_seconds, 3),
                "model": model_name,
                "high_latency": latency_seconds > HIGH_LATENCY_THRESHOLD,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            logs.append(entry)
            conn.execute(
                "UPDATE calls SET latency_logs = ? WHERE id = ?",
                (json.dumps(logs), call_id),
            )
            conn.commit()
            flag = " [HIGH LATENCY]" if entry["high_latency"] else ""
            logger.info(f"Call {call_id}: {metric_type}={latency_seconds:.3f}s ({model_name}){flag}")
        finally:
            conn.close()

    def complete_call(self, call_id: int, summary: str = ""):
        """Mark a call as complete and calculate duration.

        Args:
            call_id: The call ID.
            summary: Optional summary of the call.
        """
        conn = self._get_conn()
        try:
            row = conn.execute("SELECT start_time FROM calls WHERE id = ?", (call_id,)).fetchone()
            if not row:
                logger.warning(f"Call {call_id} not found for completion")
                return
            start_time = datetime.fromisoformat(row["start_time"])
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            conn.execute(
                "UPDATE calls SET end_time = ?, duration_seconds = ?, summary = ?, status = 'completed' WHERE id = ?",
                (end_time.isoformat(), duration, summary, call_id),
            )
            conn.commit()
            logger.info(f"Call {call_id} completed: duration={duration:.1f}s")
        finally:
            conn.close()

    def get_call(self, call_id: int) -> dict | None:
        """Retrieve a single call record.

        Args:
            call_id: The call ID.

        Returns:
            Call record as a dictionary, or None if not found.
        """
        conn = self._get_conn()
        try:
            row = conn.execute("SELECT * FROM calls WHERE id = ?", (call_id,)).fetchone()
            if not row:
                return None
            result = dict(row)
            result["transcript"] = json.loads(result["transcript"])
            result["detected_intents"] = json.loads(result["detected_intents"])
            result["latency_logs"] = json.loads(result.get("latency_logs", "[]") or "[]")
            return result
        finally:
            conn.close()

    def get_recent_calls(self, limit: int = 10) -> list[dict]:
        """Retrieve the most recent calls.

        Args:
            limit: Maximum number of calls to return.

        Returns:
            List of call records.
        """
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM calls ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            results = []
            for row in rows:
                result = dict(row)
                result["transcript"] = json.loads(result["transcript"])
                result["detected_intents"] = json.loads(result["detected_intents"])
                result["latency_logs"] = json.loads(result.get("latency_logs", "[]") or "[]")
                results.append(result)
            return results
        finally:
            conn.close()


if __name__ == "__main__":
    # Quick test of the call logger
    print(f"\n{'='*60}")
    print("Call Logger - Quick Test")
    print(f"{'='*60}\n")

    logger_instance = CallLogger(db_path="test_calls.db")

    # Start a call
    call_id = logger_instance.start_call("+15551234567", "call-test-room")
    print(f"Started call: id={call_id}")

    # Add transcript entries
    logger_instance.add_transcript_entry(call_id, "assistant", "Hello, thank you for calling Acme Corp!")
    logger_instance.add_transcript_entry(call_id, "user", "Hi, what are your hours?")
    logger_instance.add_transcript_entry(call_id, "assistant", "We're open Monday to Friday, 9 AM to 5 PM Pacific.")
    print("Added transcript entries")

    # Add intent
    logger_instance.add_detected_intent(call_id, "hours_inquiry")
    print("Added detected intent")

    # Complete call
    logger_instance.complete_call(call_id, "Caller asked about business hours.")
    print("Completed call")

    # Retrieve and display
    call = logger_instance.get_call(call_id)
    print(f"\nCall record:")
    print(f"  ID: {call['id']}")
    print(f"  Caller: {call['caller_number']}")
    print(f"  Room: {call['room_name']}")
    print(f"  Duration: {call['duration_seconds']:.1f}s")
    print(f"  Intents: {call['detected_intents']}")
    print(f"  Summary: {call['summary']}")
    print(f"  Transcript ({len(call['transcript'])} entries):")
    for entry in call["transcript"]:
        print(f"    [{entry['role']}] {entry['text']}")

    # Cleanup test db
    Path("test_calls.db").unlink(missing_ok=True)
    print(f"\n{'='*60}")
    print("All tests passed!")
    print(f"{'='*60}\n")
