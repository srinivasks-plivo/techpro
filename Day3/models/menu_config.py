"""
MenuConfiguration model - Defines the IVR menu structure.

This is the MOST IMPORTANT model because it defines the entire IVR system behavior.

Instead of hard-coding menus in Python code:
    if digit == 1:
        speak("Press 1 for sales...")

We store menu definitions in the database:
    {
        "menu_id": "main_menu",
        "message": "Press 1 for sales...",
        "digit_actions": {"1": "sales_menu"}
    }

This makes the IVR FLEXIBLE - you can change menus without restarting the app!
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from models.database import Base


class MenuConfiguration(Base):
    """
    Database table that defines all menus in the IVR system.

    Each row is one menu screen that a caller can interact with.

    Example menus:
    1. "main_menu" - Root menu with 3 options
    2. "sales_menu" - Sub-menu for sales department
    3. "operator_transfer" - Special menu that transfers the call

    All menus are connected by menu_id references, forming a tree structure:

        main_menu
        ├── sales_menu
        │   ├── sales_new_customer
        │   └── sales_existing_customer
        ├── support_menu
        └── operator_transfer
    """

    __tablename__ = "menu_configurations"

    # ===== PRIMARY KEY =====
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # ===== MENU IDENTIFICATION =====
    menu_id = Column(
        String(100),
        unique=True,  # No two menus can have the same ID
        nullable=False,
        index=True
    )
    # Example: "main_menu", "sales_menu", "operator_transfer"
    # This is used everywhere to reference this menu

    # ===== MENU HIERARCHY =====
    parent_menu_id = Column(
        String(100),
        nullable=True,  # NULL means this is a root menu
        index=True
    )
    # Example: If this is "sales_menu", parent is "main_menu"
    # NULL for "main_menu" because it has no parent
    # Used to track where callers came from (breadcrumb trail)

    # ===== MENU CLASSIFICATION =====
    menu_type = Column(
        String(50),
        nullable=False,
        default='menu'
    )
    # Options:
    # - 'menu': Normal menu (user presses digits to navigate)
    # - 'action': Special menu that does something (transfer, hangup, etc.)
    # - 'submenu': Just like 'menu' but helps organize logically

    # ===== DISPLAY INFORMATION =====
    title = Column(
        String(255),
        nullable=False
    )
    # Human-readable title (for admin UI)
    # Example: "Main Menu", "Sales Department"

    message = Column(
        Text,  # Unlimited length text
        nullable=False
    )
    # The message spoken to the caller via text-to-speech
    # Example: "Welcome to our IVR. Press 1 for Sales, Press 2 for Support"

    # ===== AUDIO CONFIGURATION =====
    audio_url = Column(
        String(500),
        nullable=True
    )
    # Optional: Use a pre-recorded audio file instead of TTS
    # Example: "https://cdn.example.com/welcome.mp3"
    # If provided, we use <Play> instead of <Speak> in Plivo

    language = Column(
        String(10),
        nullable=False,
        default='en-US'
    )
    # Language for text-to-speech
    # Examples: 'en-US', 'en-GB', 'es-ES', 'fr-FR'

    voice = Column(
        String(50),
        nullable=False,
        default='WOMAN'
    )
    # Voice for TTS
    # Plivo options: 'WOMAN', 'MAN'

    # ===== INPUT CONFIGURATION =====
    max_digits = Column(
        Integer,
        nullable=False,
        default=1
    )
    # How many digits can the user enter?
    # Usually 1 (user presses ONE digit: 1, 2, 3, etc.)
    # Could be 4 for PIN entry, 10 for account number

    timeout = Column(
        Integer,  # Seconds
        nullable=False,
        default=5
    )
    # How long to wait for user to press something
    # After timeout seconds of silence, what happens?
    # That's controlled by timeout_menu_id

    # ===== DIGIT ROUTING =====
    digit_actions = Column(
        JSON,
        nullable=True
    )
    # Mapping of digit -> next action
    # Example:
    # {
    #     "1": "sales_menu",
    #     "2": "support_menu",
    #     "3": "billing_menu",
    #     "0": "operator_transfer"
    # }
    # When user presses 1, go to sales_menu

    # ===== ERROR HANDLING =====
    invalid_input_menu_id = Column(
        String(100),
        nullable=True
    )
    # What menu to show if user presses an invalid digit?
    # Example: If only 1-3 are valid and user presses 5,
    #          show the invalid_input_menu_id menu
    # Usually a message like "Invalid input. Please try again."

    timeout_menu_id = Column(
        String(100),
        nullable=True
    )
    # What menu to show if user doesn't press anything (timeout)?
    # Usually a message like "We didn't hear you. Please try again."

    # ===== ACTION CONFIGURATION =====
    action_type = Column(
        String(50),
        nullable=True
    )
    # What does this menu do?
    # Options:
    # - 'navigate': Go to another menu (default)
    # - 'transfer': Transfer call to a phone number
    # - 'hangup': End the call
    # - 'api_call': Call an external API
    # - 'record': Record the caller's message

    action_config = Column(
        JSON,
        nullable=True
    )
    # Configuration for the action
    # Examples for transfer:
    # {
    #     "transfer_number": "+15551234567",
    #     "timeout": 30
    # }

    # ===== STATUS =====
    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )
    # Is this menu enabled?
    # Set to False to disable a menu temporarily without deleting it

    priority = Column(
        Integer,
        nullable=False,
        default=0
    )
    # Display priority (for UI)
    # Higher number = higher priority

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
            f"<MenuConfiguration("
            f"menu_id={self.menu_id}, "
            f"type={self.menu_type}, "
            f"active={self.is_active}"
            f")>"
        )

    def is_leaf_menu(self):
        """
        Check if this is a leaf menu (no children, dead end).

        A leaf menu is one where no other menu references it as parent.

        Returns:
            bool: True if no children

        Note: We'd need to query the database to know for sure.
              This is a simplified version.
        """
        return self.action_type is not None

    def get_digit_option(self, digit):
        """
        Get the next menu for a specific digit.

        Args:
            digit (str): The digit pressed (0-9, *, #)

        Returns:
            str: Menu ID to go to, or None if digit not valid

        Example:
            menu.digit_actions = {"1": "sales_menu", "2": "support_menu"}
            menu.get_digit_option("1")  # Returns "sales_menu"
            menu.get_digit_option("9")  # Returns None
        """
        if self.digit_actions and digit in self.digit_actions:
            return self.digit_actions[digit]
        return None

    def validate_digit(self, digit):
        """
        Check if a digit is valid for this menu.

        Args:
            digit (str): The digit pressed

        Returns:
            bool: True if digit is a valid option

        Example:
            menu.validate_digit("1")  # True if "1" in digit_actions
            menu.validate_digit("9")  # False if "9" not in digit_actions
        """
        if self.digit_actions:
            return digit in self.digit_actions
        return False

    def to_dict(self):
        """Convert to dictionary for JSON responses."""
        return {
            'menu_id': self.menu_id,
            'title': self.title,
            'message': self.message,
            'max_digits': self.max_digits,
            'timeout': self.timeout,
            'digit_actions': self.digit_actions,
            'action_type': self.action_type,
            'is_active': self.is_active,
        }
