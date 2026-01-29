"""
CallerHistory model - Aggregated information about each caller.

While CallLog stores details about EACH call,
CallerHistory stores SUMMARY information about a caller:
- Total calls from this number
- First call timestamp
- Last call timestamp
- Average duration
- Language preference
- Last menu they completed

Example: If someone called 5 times, there are 5 CallLog rows,
but only 1 CallerHistory row that summarizes all 5 calls.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from models.database import Base


class CallerHistory(Base):
    """
    Database table that aggregates information about callers.

    This is like a "Customer Profile" for each phone number.
    It helps us:
    - Recognize repeat callers
    - Track their preferences
    - Know how many times they've called
    - Personalize their experience
    """

    __tablename__ = "caller_history"  # Table name in PostgreSQL

    # ===== PRIMARY KEY =====
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # ===== CALLER IDENTIFICATION =====
    phone_number = Column(
        String(20),
        unique=True,  # Only one record per phone number
        nullable=False,
        index=True  # Fast lookups by phone number
    )
    # Example: "+15551234567"
    # This is the unique identifier for this caller

    # ===== CALL TRACKING =====
    first_call_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    # When did this person first call us?

    last_call_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow  # Updates every time they call
    )
    # When did they last call?

    total_calls = Column(
        Integer,
        nullable=False,
        default=1
    )
    # How many times have they called?
    # Example: 5

    total_duration = Column(
        Integer,  # Measured in seconds
        nullable=False,
        default=0
    )
    # Total time spent in IVR across all calls
    # Example: 450 = 7.5 minutes total

    # ===== PREFERENCES =====
    preferred_language = Column(
        String(10),
        nullable=True,
        default='en'
    )
    # Example: 'en' (English), 'es' (Spanish), 'fr' (French)
    # We could use this to greet them in their language

    # ===== INTERACTION HISTORY =====
    last_menu_completed = Column(
        String(100),
        nullable=True
    )
    # What's the last menu they completed?
    # Example: 'billing_payment'
    # Useful if they call back - we can ask "continuing from billing?"

    # ===== FLEXIBLE DATA =====
    extra_data = Column(
        JSON,
        nullable=True
    )
    # Any custom data we want to store about this caller
    # Examples:
    # {
    #     "account_number": "ACC123456",
    #     "customer_tier": "premium",
    #     "vip": true,
    #     "notes": "Prefers email over call"
    # }

    # ===== TIMESTAMPS =====
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ===== METHODS =====
    def __repr__(self):
        """String representation for debugging."""
        return (
            f"<CallerHistory("
            f"phone_number={self.phone_number}, "
            f"total_calls={self.total_calls}, "
            f"total_duration={self.total_duration}s"
            f")>"
        )

    def average_call_duration(self):
        """
        Calculate average call duration in seconds.

        Returns:
            float: Average seconds per call
        """
        if self.total_calls > 0:
            return self.total_duration / self.total_calls
        return 0

    def is_returning_caller(self):
        """
        Check if this is a repeat caller.

        A returning caller is someone who has called more than once.

        Returns:
            bool: True if total_calls > 1
        """
        return self.total_calls > 1

    def update_from_call_log(self, duration):
        """
        Update this record after a call completes.

        Args:
            duration (int): Duration of the call in seconds

        Example:
            caller.update_from_call_log(180)  # 3 minute call
            # Now total_calls = 2, total_duration = 360, last_call_at = now
        """
        self.total_calls += 1
        self.total_duration += duration
        self.last_call_at = datetime.utcnow()

    def to_dict(self):
        """Convert to dictionary for JSON responses."""
        return {
            'phone_number': self.phone_number,
            'total_calls': self.total_calls,
            'total_duration': self.total_duration,
            'average_duration': self.average_call_duration(),
            'first_call_at': self.first_call_at.isoformat() if self.first_call_at else None,
            'last_call_at': self.last_call_at.isoformat() if self.last_call_at else None,
            'preferred_language': self.preferred_language,
            'is_returning_caller': self.is_returning_caller(),
        }
