"""
Redis Service - Manages temporary call session data.

WHY REDIS?
===========
- Fast: Data in RAM, microsecond response times
- Temporary: Perfect for active call sessions
- TTL: Auto-expires old sessions
- Simple: JSON strings are easy to work with

THE BIG PICTURE:
================
While a call is active, we store the session in Redis:
- Current menu ID
- Menu history (breadcrumb trail)
- User inputs (digits pressed)
- Call metadata

When call ends:
- Session data → CallLog model (permanent)
- Session deleted from Redis (cleanup)

FLOW:
  Call arrives → Create Redis session
  User presses digit → Update Redis session
  Call ends → Save to database, delete session

Think of Redis as a "scratchpad" for the call.
Permanent data goes to PostgreSQL models.
"""

import json
import redis
from datetime import datetime
from config import get_config

# Get configuration
config = get_config()


class RedisSessionService:
    """
    Manage call sessions in Redis.

    Each active call has a session stored in Redis with TTL (time to live).
    After 30 minutes of inactivity, the session automatically expires.
    """

    def __init__(self):
        """Initialize Redis connection."""
        # Connect to Redis using configuration
        self.redis_client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True,  # Return strings instead of bytes
            socket_connect_timeout=5,  # 5 second timeout
            socket_keepalive=True,  # Keep connection alive
        )

        # Verify connection works
        try:
            self.redis_client.ping()
            print("✓ Redis connection successful")
        except Exception as e:
            print(f"✗ Redis connection failed: {e}")
            raise

    # ===== SESSION CRUD OPERATIONS =====

    def create_session(self, call_uuid, from_number, to_number):
        """
        Create a new call session in Redis.

        This is called when someone calls your Plivo number.

        Args:
            call_uuid (str): Unique call ID from Plivo
            from_number (str): Caller's phone number (e.g., "+15551234567")
            to_number (str): Your Plivo phone number

        Returns:
            dict: The created session data

        Example:
            session = redis_service.create_session(
                call_uuid="abc123",
                from_number="+15551234567",
                to_number="+15559876543"
            )
            # Returns:
            # {
            #     "call_uuid": "abc123",
            #     "from_number": "+15551234567",
            #     "current_menu_id": "main_menu",
            #     "menu_history": ["main_menu"],
            #     "user_inputs": [],
            #     "start_time": "2026-01-29T10:00:00Z",
            #     "state": "active"
            # }
        """
        # Initialize session structure
        session_data = {
            "call_uuid": call_uuid,
            "from_number": from_number,
            "to_number": to_number,
            "current_menu_id": "main_menu",  # Always start at main menu
            "menu_history": ["main_menu"],  # Breadcrumb trail of menus
            "user_inputs": [],  # Digits pressed so far
            "start_time": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "state": "active",  # State: active, completed, abandoned, error
        }

        # Store in Redis with TTL (time to live)
        session_key = f"ivr:session:{call_uuid}"
        self.redis_client.setex(
            session_key,
            config.SESSION_TTL,  # 1800 seconds (30 minutes)
            json.dumps(session_data),  # Convert dict to JSON string
        )

        print(f"📱 Session created: {call_uuid}")
        return session_data

    def get_session(self, call_uuid):
        """
        Retrieve a session from Redis.

        Args:
            call_uuid (str): Unique call ID

        Returns:
            dict: Session data, or None if not found

        Example:
            session = redis_service.get_session("abc123")
            if session:
                print(session["current_menu_id"])  # "main_menu"
            else:
                print("Session expired or not found")
        """
        session_key = f"ivr:session:{call_uuid}"

        # Get from Redis
        session_json = self.redis_client.get(session_key)

        if session_json is None:
            print(f"⚠️  Session not found: {call_uuid}")
            return None

        # Parse JSON string back to dict
        session_data = json.loads(session_json)
        print(f"📖 Session retrieved: {call_uuid}")
        return session_data

    def update_session(self, call_uuid, updates):
        """
        Update an existing session with new data.

        This is called whenever we need to change the session
        (new menu, new input, etc.)

        Args:
            call_uuid (str): Unique call ID
            updates (dict): Fields to update
                Example: {"current_menu_id": "sales_menu", "last_activity": "..."}

        Returns:
            dict: Updated session data, or None if session not found

        Example:
            session = redis_service.update_session(
                "abc123",
                {
                    "current_menu_id": "sales_menu",
                    "menu_history": ["main_menu", "sales_menu"]
                }
            )
        """
        # First, get current session
        session = self.get_session(call_uuid)
        if session is None:
            return None

        # Update with new data
        session.update(updates)
        session["last_activity"] = datetime.utcnow().isoformat()

        # Save back to Redis
        session_key = f"ivr:session:{call_uuid}"
        self.redis_client.setex(
            session_key,
            config.SESSION_TTL,
            json.dumps(session),
        )

        print(f"🔄 Session updated: {call_uuid}")
        return session

    def delete_session(self, call_uuid):
        """
        Delete a session from Redis.

        Called when call ends to clean up.

        Args:
            call_uuid (str): Unique call ID

        Returns:
            bool: True if deleted, False if didn't exist

        Example:
            deleted = redis_service.delete_session("abc123")
            if deleted:
                print("Session cleaned up")
        """
        session_key = f"ivr:session:{call_uuid}"
        result = self.redis_client.delete(session_key)
        if result > 0:
            print(f"🗑️  Session deleted: {call_uuid}")
            return True
        else:
            print(f"⚠️  Session already deleted or didn't exist: {call_uuid}")
            return False

    # ===== SESSION MANIPULATION =====

    def add_user_input(self, call_uuid, menu_id, digit):
        """
        Record that the user pressed a digit.

        This creates a record of what button they pressed and when,
        in which menu they pressed it.

        Args:
            call_uuid (str): Unique call ID
            menu_id (str): Which menu were they in? ("main_menu", "sales_menu")
            digit (str): What digit did they press? ("1", "2", "*", "#")

        Returns:
            dict: Updated session, or None if session not found

        Example:
            session = redis_service.add_user_input(
                "abc123",
                "main_menu",
                "1"
            )
            # Now session["user_inputs"] = [
            #     {"menu_id": "main_menu", "digit": "1", "timestamp": "2026-01-29T10:00:05Z"}
            # ]
        """
        session = self.get_session(call_uuid)
        if session is None:
            return None

        # Add input record
        input_record = {
            "menu_id": menu_id,
            "digit": digit,
            "timestamp": datetime.utcnow().isoformat(),
        }
        session["user_inputs"].append(input_record)

        # Save back
        return self.update_session(call_uuid, {"user_inputs": session["user_inputs"]})

    def set_current_menu(self, call_uuid, menu_id):
        """
        Change the current menu the caller is in.

        Args:
            call_uuid (str): Unique call ID
            menu_id (str): New menu ID ("sales_menu", "support_menu", etc.)

        Returns:
            dict: Updated session, or None if not found

        Example:
            session = redis_service.set_current_menu("abc123", "sales_menu")
        """
        session = self.get_session(call_uuid)
        if session is None:
            return None

        # Add to history (breadcrumb trail)
        session["menu_history"].append(menu_id)

        # Update current menu
        return self.update_session(
            call_uuid,
            {
                "current_menu_id": menu_id,
                "menu_history": session["menu_history"],
            },
        )

    def mark_call_completed(self, call_uuid):
        """
        Mark a call as completed (successful).

        Args:
            call_uuid (str): Unique call ID

        Returns:
            dict: Updated session, or None if not found
        """
        return self.update_session(call_uuid, {"state": "completed"})

    def mark_call_abandoned(self, call_uuid):
        """
        Mark a call as abandoned (caller hung up).

        Args:
            call_uuid (str): Unique call ID

        Returns:
            dict: Updated session, or None if not found
        """
        return self.update_session(call_uuid, {"state": "abandoned"})

    def mark_call_error(self, call_uuid, error_message):
        """
        Mark a call as having an error.

        Args:
            call_uuid (str): Unique call ID
            error_message (str): What went wrong?

        Returns:
            dict: Updated session, or None if not found
        """
        return self.update_session(
            call_uuid,
            {
                "state": "error",
                "error_message": error_message,
            },
        )

    # ===== SESSION ANALYSIS =====

    def get_menu_history(self, call_uuid):
        """
        Get the menu path (breadcrumb trail) for a call.

        Args:
            call_uuid (str): Unique call ID

        Returns:
            list: Menu IDs in order visited, or None if session not found

        Example:
            path = redis_service.get_menu_history("abc123")
            # Returns: ["main_menu", "sales_menu", "sales_new_customer"]
        """
        session = self.get_session(call_uuid)
        if session is None:
            return None
        return session["menu_history"]

    def get_user_inputs(self, call_uuid):
        """
        Get all digits pressed by the user.

        Args:
            call_uuid (str): Unique call ID

        Returns:
            list: Input records with menu_id, digit, timestamp

        Example:
            inputs = redis_service.get_user_inputs("abc123")
            # Returns:
            # [
            #     {"menu_id": "main_menu", "digit": "1", "timestamp": "2026-01-29T10:00:05Z"},
            #     {"menu_id": "sales_menu", "digit": "1", "timestamp": "2026-01-29T10:00:08Z"}
            # ]
        """
        session = self.get_session(call_uuid)
        if session is None:
            return None
        return session["user_inputs"]

    def get_call_duration(self, call_uuid):
        """
        Calculate how long the call has been active.

        Args:
            call_uuid (str): Unique call ID

        Returns:
            float: Duration in seconds, or None if session not found

        Example:
            duration = redis_service.get_call_duration("abc123")
            print(f"Call duration so far: {duration:.1f} seconds")
        """
        session = self.get_session(call_uuid)
        if session is None:
            return None

        start_time = datetime.fromisoformat(session["start_time"])
        current_time = datetime.utcnow()
        duration = (current_time - start_time).total_seconds()
        return duration

    # ===== HEALTH CHECK =====

    def ping(self):
        """
        Test Redis connection.

        Returns:
            bool: True if Redis is responsive, False otherwise

        Example:
            if redis_service.ping():
                print("Redis is working!")
            else:
                print("Redis is down!")
        """
        try:
            return self.redis_client.ping()
        except Exception as e:
            print(f"Redis ping failed: {e}")
            return False


# ===== SINGLETON INSTANCE =====
# Create a single instance to use throughout the app
redis_service = RedisSessionService()


# ===== EXAMPLE USAGE =====
if __name__ == "__main__":
    """
    Example: How to use the Redis service

    This shows a complete call flow:
    1. Call arrives
    2. Create session
    3. User presses digit
    4. Update session
    5. Navigate to new menu
    6. Call ends
    7. Clean up
    """

    # Step 1: Incoming call
    print("\n=== INCOMING CALL ===")
    session = redis_service.create_session(
        call_uuid="test-call-123",
        from_number="+15551234567",
        to_number="+15559876543",
    )
    print(f"Session created: {session}")

    # Step 2: Check session
    print("\n=== CHECK SESSION ===")
    session = redis_service.get_session("test-call-123")
    print(f"Current menu: {session['current_menu_id']}")
    print(f"Menu history: {session['menu_history']}")

    # Step 3: User presses digit
    print("\n=== USER PRESSES 1 ===")
    redis_service.add_user_input("test-call-123", "main_menu", "1")

    # Step 4: Navigate to sales menu
    print("\n=== NAVIGATE TO SALES ===")
    redis_service.set_current_menu("test-call-123", "sales_menu")

    # Step 5: User presses another digit
    print("\n=== USER PRESSES 1 AGAIN ===")
    redis_service.add_user_input("test-call-123", "sales_menu", "1")

    # Step 6: Check final state
    print("\n=== FINAL STATE ===")
    session = redis_service.get_session("test-call-123")
    print(f"Menu history: {session['menu_history']}")
    print(f"User inputs: {session['user_inputs']}")
    print(f"Duration: {redis_service.get_call_duration('test-call-123'):.1f}s")

    # Step 7: Call ends
    print("\n=== CALL ENDS ===")
    redis_service.mark_call_completed("test-call-123")

    # Step 8: Clean up
    print("\n=== CLEANUP ===")
    redis_service.delete_session("test-call-123")
    print("Session deleted")
