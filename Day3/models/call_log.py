"""
CallLog model - Stores information about each phone call.

When a call ends, we save all details to this table:
- Who called (from_number)
- Who was called (to_number)
- When it started and ended
- What menus they navigated through
- What buttons they pressed

This creates a permanent record of all calls for analytics, debugging, etc.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, DECIMAL, JSON
from models.database import Base


class CallLog(Base):
    """
    Database table that stores information about completed calls.

    Think of this like a phone bill - it records:
    - Who called
    - When
    - How long
    - What they did
    """

    __tablename__ = "call_logs"  # The actual table name in PostgreSQL

    # ===== PRIMARY KEY =====
    # Every row needs a unique ID
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True  # Automatically increment: 1, 2, 3, etc.
    )

    # ===== CALL IDENTIFIERS =====
    # These uniquely identify this call

    call_uuid = Column(
        String(255),
        unique=True,  # No two calls can have the same UUID
        nullable=False,
        index=True  # Create an index for fast lookups
    )
    # Example: "4f3a4e5c-b2d8-4a7f-9c1e-3b8f6a9d2e1c"
    # Plivo generates this automatically for each call

    # ===== PHONE NUMBERS =====
    from_number = Column(
        String(20),
        nullable=False,
        index=True
    )
    # Example: "+15551234567" - The phone number that called us

    to_number = Column(
        String(20),
        nullable=False
    )
    # Example: "+15559876543" - Our Plivo phone number

    # ===== CALL TIMING =====
    start_time = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,  # Automatically set to current time
        index=True
    )
    # When the call started

    answer_time = Column(
        DateTime,
        nullable=True  # Might be NULL if call wasn't answered
    )
    # When the call was answered (might be different from start_time)

    end_time = Column(
        DateTime,
        nullable=True
    )
    # When the call ended

    # ===== CALL STATISTICS =====
    duration = Column(
        Integer,  # Measured in seconds
        nullable=True
    )
    # Example: 180 = 3 minutes
    # Calculate as: (end_time - start_time) in seconds

    call_status = Column(
        String(50),
        nullable=False,
        default='active'  # Options: 'active', 'completed', 'abandoned', 'error'
    )

    hangup_cause = Column(
        String(100),
        nullable=True
    )
    # Why the call ended. Examples: 'NORMAL_CLEARING', 'USER_BUSY', 'NO_ANSWER'
    # Plivo provides this information

    # ===== CALL COST =====
    total_cost = Column(
        DECIMAL(10, 4),  # Up to 10 digits, 4 decimal places
        nullable=True
    )
    # Example: 0.0250 = 2.5 cents
    # Plivo bills based on call duration

    # ===== IVR SPECIFIC DATA =====
    # This is the interesting part - what the caller actually did

    menu_path = Column(
        JSON,
        nullable=True
    )
    # Array of menu IDs the caller visited, in order
    # Example: ["main_menu", "sales_menu", "sales_new_customer"]
    # This shows the path the caller took through the IVR

    user_inputs = Column(
        JSON,
        nullable=True
    )
    # Array of digit inputs with timestamps
    # Example:
    # [
    #     {"menu_id": "main_menu", "digit": "1", "timestamp": "2026-01-29T10:00:00Z"},
    #     {"menu_id": "sales_menu", "digit": "1", "timestamp": "2026-01-29T10:00:03Z"}
    # ]
    # This shows exactly what buttons they pressed and when

    # ===== TIMESTAMPS =====
    # Always track when records are created and updated
    # Useful for debugging and analytics

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow  # Automatically set when created
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow  # Automatically updated when changed
    )

    # ===== METHODS =====
    def __repr__(self):
        """
        String representation of a CallLog for debugging.

        When you print a CallLog object, this is what shows up.
        """
        return (
            f"<CallLog("
            f"id={self.id}, "
            f"call_uuid={self.call_uuid[:8]}..., "
            f"from={self.from_number}, "
            f"duration={self.duration}s"
            f")>"
        )

    def calculate_duration(self):
        """
        Calculate call duration in seconds.

        If both start_time and end_time are set, calculate the difference.

        Returns:
            int: Duration in seconds, or None if not both times are set
        """
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds())
        return None

    def to_dict(self):
        """
        Convert this CallLog to a dictionary (useful for JSON responses).

        Returns:
            dict: All fields as a dictionary
        """
        return {
            'id': self.id,
            'call_uuid': self.call_uuid,
            'from_number': self.from_number,
            'to_number': self.to_number,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'call_status': self.call_status,
            'menu_path': self.menu_path,
            'user_inputs': self.user_inputs,
        }
