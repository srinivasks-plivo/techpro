"""
IVR Service - Orchestrates the entire IVR call flow.

THE CONDUCTOR:
===============
Redis Service = Session memory (what's happening NOW)
Plivo Service = XML generation (how to respond)
IVR Service = The orchestrator (what should happen NEXT)

IVR Service connects everything:
- Loads menus from database (MenuConfiguration model)
- Reads current session from Redis
- Validates user input
- Determines next action
- Generates XML response (via Plivo Service)
- Updates session (via Redis Service)

THE BIG PICTURE:
=================
Incoming call → Load menu → Generate XML
                    ↑           ↓
                    └─ User presses digit ← Generate response

This service contains all the IVR BUSINESS LOGIC.
"""

from models import MenuConfiguration
from models.database import SessionLocal
from services.redis_service import redis_service
from services.plivo_service import plivo_service
from config import get_config

# Get configuration
config = get_config()


class IVRService:
    """
    Orchestrate the IVR call flow.

    This is where all the decision-making happens:
    - Which menu should the user see?
    - Are their inputs valid?
    - What should happen next?
    """

    def __init__(self):
        """Initialize IVR service."""
        # We'll get database sessions as needed
        pass

    # ===== MAIN CALL HANDLERS =====

    def handle_incoming_call(self, call_uuid, from_number, to_number):
        """
        Handle incoming call.

        This is called when someone dials your Plivo number.

        Flow:
        1. Create Redis session
        2. Load main menu from database
        3. Generate XML response
        4. Return XML to Plivo

        Args:
            call_uuid (str): Unique call ID from Plivo
            from_number (str): Caller's phone number
            to_number (str): Your Plivo number

        Returns:
            str: XML response for Plivo

        Example:
            xml = ivr_service.handle_incoming_call(
                "abc123",
                "+15551234567",
                "+15559876543"
            )
            # Plivo will speak the main menu message
        """
        print(f"\n📱 INCOMING CALL: {from_number}")

        # Step 1: Create session in Redis
        session = redis_service.create_session(call_uuid, from_number, to_number)

        # Step 2: Load main menu
        menu = self._get_menu_config("main_menu")
        if menu is None:
            print("❌ Error: main_menu not found in database!")
            return plivo_service.generate_hangup_xml(
                "Sorry, our system is unavailable. Please try later."
            )

        # Step 3: Generate and return XML
        xml = plivo_service.generate_menu_xml(
            message=menu.message,
            timeout=menu.timeout,
            max_digits=menu.max_digits,
            action_url=f"{config.WEBHOOK_BASE_URL}/voice/input"
        )

        print(f"✓ Returning main menu XML")
        return xml

    def handle_digit_input(self, call_uuid, digit):
        """
        Handle user pressing a digit.

        This is called when Plivo detects the user pressed a button.

        Flow:
        1. Get current session from Redis
        2. Get current menu from database
        3. Validate digit (is it a valid option?)
        4. Record input in session
        5. Determine action (menu, transfer, hangup, etc.)
        6. Generate XML response
        7. Update session
        8. Return XML

        Args:
            call_uuid (str): Unique call ID
            digit (str): What digit did they press? ("1", "2", "*", "#")

        Returns:
            str: XML response for Plivo

        Example:
            xml = ivr_service.handle_digit_input("abc123", "1")
            # User pressed 1, navigate to next menu
        """
        print(f"\n🔘 DIGIT INPUT: {digit}")

        # Step 1: Get session
        session = redis_service.get_session(call_uuid)
        if session is None:
            print("❌ Error: Session not found (expired?)")
            return plivo_service.generate_hangup_xml(
                "Your session has expired. Please call back."
            )

        # Step 2: Get current menu
        current_menu_id = session["current_menu_id"]
        menu = self._get_menu_config(current_menu_id)
        if menu is None:
            print(f"❌ Error: Menu not found: {current_menu_id}")
            return plivo_service.generate_hangup_xml("System error. Please try later.")

        # Step 3: Validate digit
        if not menu.validate_digit(digit):
            print(f"❌ Invalid digit: {digit} not in {menu.digit_actions}")
            # User pressed invalid digit - show error
            invalid_menu_id = menu.invalid_input_menu_id
            if invalid_menu_id:
                invalid_menu = self._get_menu_config(invalid_menu_id)
                if invalid_menu:
                    xml = plivo_service.generate_menu_xml(
                        message=invalid_menu.message,
                        timeout=invalid_menu.timeout,
                        action_url=f"{config.WEBHOOK_BASE_URL}/voice/input"
                    )
                    return xml
            # Fallback: generic error
            return plivo_service.generate_invalid_input_xml()

        # Step 4: Record input
        redis_service.add_user_input(call_uuid, current_menu_id, digit)
        print(f"✓ Recorded digit {digit} in session")

        # Step 5: Determine action
        next_menu_id = menu.get_digit_option(digit)
        print(f"🎯 Next action: {next_menu_id}")

        # Step 6: Generate response based on action type
        if menu.action_type == "transfer":
            # Transfer to a phone number
            print("📞 Action: TRANSFER")
            transfer_number = menu.action_config.get("transfer_number")
            xml = plivo_service.generate_transfer_xml(transfer_number)

        elif menu.action_type == "hangup":
            # End the call
            print("📵 Action: HANGUP")
            xml = plivo_service.generate_hangup_xml(menu.message)

        elif menu.action_type == "menu" or next_menu_id:
            # Navigate to next menu (most common)
            print("🗂️  Action: NAVIGATE MENU")
            next_menu = self._get_menu_config(next_menu_id)
            if next_menu is None:
                print(f"❌ Error: Next menu not found: {next_menu_id}")
                return plivo_service.generate_hangup_xml("System error.")

            # Update session with new menu
            redis_service.set_current_menu(call_uuid, next_menu_id)
            print(f"✓ Updated session to menu: {next_menu_id}")

            # Generate XML for next menu
            xml = plivo_service.generate_menu_xml(
                message=next_menu.message,
                timeout=next_menu.timeout,
                max_digits=next_menu.max_digits,
                action_url=f"{config.WEBHOOK_BASE_URL}/voice/input"
            )

        else:
            # Unknown action
            print("⚠️  Warning: Unknown action type")
            xml = plivo_service.generate_hangup_xml("Thank you for calling.")

        print(f"✓ Returning response XML")
        return xml

    def handle_hangup(self, call_uuid, hangup_cause=None, duration=None):
        """
        Handle call end.

        This is called when Plivo detects the call has ended
        (user hung up, transfer ended, etc.)

        Flow:
        1. Get session from Redis
        2. Mark call as completed in session
        3. Save session to CallLog (permanent storage)
        4. Update CallerHistory
        5. Delete session from Redis (cleanup)

        Args:
            call_uuid (str): Unique call ID
            hangup_cause (str): Why did call end? ("USER_HANGUP", etc.)
            duration (int): Call duration in seconds

        Returns:
            None

        Example:
            ivr_service.handle_hangup(
                "abc123",
                hangup_cause="NORMAL_CLEARING",
                duration=330
            )
        """
        print(f"\n📵 CALL HANGUP: {call_uuid}")

        # Step 1: Get session
        session = redis_service.get_session(call_uuid)
        if session is None:
            print("⚠️  Session already expired/deleted")
            return

        # Step 2: Mark call as completed
        redis_service.mark_call_completed(call_uuid)
        print(f"✓ Marked call as completed")

        # Step 3: Save to database (permanent storage)
        self._save_call_to_database(call_uuid, session, hangup_cause, duration)

        # Step 4: Update caller history
        self._update_caller_history(session["from_number"], duration)

        # Step 5: Clean up session
        redis_service.delete_session(call_uuid)
        print(f"✓ Session cleaned up")

        print(f"✓ Call processing complete")

    # ===== HELPER METHODS =====

    def _get_menu_config(self, menu_id):
        """
        Load menu configuration from database.

        Args:
            menu_id (str): Menu ID to load

        Returns:
            MenuConfiguration object, or None if not found
        """
        db = SessionLocal()
        try:
            menu = db.query(MenuConfiguration).filter_by(menu_id=menu_id).first()
            if menu:
                print(f"📖 Loaded menu: {menu_id}")
            else:
                print(f"❌ Menu not found: {menu_id}")
            return menu
        finally:
            db.close()

    def _save_call_to_database(self, call_uuid, session, hangup_cause, duration):
        """
        Save call session to CallLog table (permanent storage).

        Args:
            call_uuid (str): Call ID
            session (dict): Session data from Redis
            hangup_cause (str): Why did call end
            duration (int): Call duration in seconds
        """
        from models import CallLog
        from datetime import datetime, timedelta

        db = SessionLocal()
        try:
            # Calculate timestamps
            start_time = datetime.fromisoformat(session["start_time"])
            end_time = start_time + timedelta(seconds=duration) if duration else datetime.utcnow()

            # Create CallLog record
            call_log = CallLog(
                call_uuid=call_uuid,
                from_number=session["from_number"],
                to_number=session["to_number"],
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                menu_path=session["menu_history"],
                user_inputs=session["user_inputs"],
                call_status="completed",
                hangup_cause=hangup_cause,
            )

            db.add(call_log)
            db.commit()
            print(f"✓ Saved call to CallLog: {call_uuid}")

        except Exception as e:
            print(f"❌ Error saving call: {e}")
            db.rollback()
        finally:
            db.close()

    def _update_caller_history(self, phone_number, duration):
        """
        Update caller history with new call data.

        Args:
            phone_number (str): Caller's phone number
            duration (int): Call duration in seconds
        """
        from models import CallerHistory
        from datetime import datetime

        db = SessionLocal()
        try:
            # Try to find existing caller
            caller = db.query(CallerHistory).filter_by(
                phone_number=phone_number
            ).first()

            if caller:
                # Update existing caller
                caller.total_calls += 1
                if duration:
                    caller.total_duration += duration
                caller.last_call_at = datetime.utcnow()
                print(f"✓ Updated CallerHistory: {caller.total_calls} calls")
            else:
                # Create new caller
                caller = CallerHistory(
                    phone_number=phone_number,
                    first_call_at=datetime.utcnow(),
                    last_call_at=datetime.utcnow(),
                    total_calls=1,
                    total_duration=duration or 0,
                )
                db.add(caller)
                print(f"✓ Created new CallerHistory entry")

            db.commit()

        except Exception as e:
            print(f"❌ Error updating caller history: {e}")
            db.rollback()
        finally:
            db.close()


# ===== SINGLETON INSTANCE =====
ivr_service = IVRService()


# ===== EXAMPLE USAGE =====
if __name__ == "__main__":
    """
    Example: How IVR Service orchestrates a call

    This shows the complete flow:
    1. Incoming call
    2. User presses digit
    3. Navigate to next menu
    4. User presses another digit
    5. Call ends and is saved
    """

    print("\n" + "="*60)
    print("IVR SERVICE EXAMPLE - SIMULATING A CALL")
    print("="*60)

    # Simulated call parameters
    call_uuid = "example-call-001"
    from_number = "+15551234567"
    to_number = "+15559876543"

    print("\n[1] INCOMING CALL")
    print(f"   From: {from_number}")
    print(f"   To: {to_number}")
    print(f"   UUID: {call_uuid}")
    # xml = ivr_service.handle_incoming_call(call_uuid, from_number, to_number)
    # print(f"   Response: {xml[:100]}...")

    print("\n[2] USER PRESSES DIGIT 1")
    # xml = ivr_service.handle_digit_input(call_uuid, "1")
    # print(f"   Response: {xml[:100]}...")

    print("\n[3] USER PRESSES DIGIT 1 AGAIN")
    # xml = ivr_service.handle_digit_input(call_uuid, "1")
    # print(f"   Response: {xml[:100]}...")

    print("\n[4] CALL ENDS")
    # ivr_service.handle_hangup(call_uuid, "NORMAL_CLEARING", 300)

    print("\nNote: Examples are commented out because they require:")
    print("  - Database initialized with menus")
    print("  - Redis running")
    print("  - Proper configuration")
