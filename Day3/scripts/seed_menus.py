"""
Seed Default Menus - Simplified IVR menu structure

MENU FLOW:
==========
Main Menu:
  Press 1 -> Transfer to Sales
  Press 2 -> Transfer to Support
  Other   -> Invalid input, retry

HOW TO RUN:
===========
python scripts/seed_menus.py
"""

import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, '/Users/intern-srinivas/Desktop/TECHPRO/Day3')

from models.database import SessionLocal
from models import MenuConfiguration
from config import get_config

config = get_config()

def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_success(text):
    """Print success message."""
    print(f"✓ {text}")

def print_error(text):
    """Print error message."""
    print(f"✗ {text}")

def print_info(text):
    """Print info message."""
    print(f"→ {text}")

def create_menu(db, menu_id, parent_menu_id, title, message, digit_actions=None,
                action_type='menu', action_config=None, timeout=5, max_digits=1):
    """Helper function to create a menu configuration."""
    menu = MenuConfiguration(
        menu_id=menu_id,
        parent_menu_id=parent_menu_id,
        title=title,
        message=message,
        digit_actions=digit_actions,
        action_type=action_type,
        action_config=action_config,
        timeout=timeout,
        max_digits=max_digits,
        is_active=True
    )
    db.add(menu)
    return menu

def main():
    """Main function to seed simplified menus."""

    print_header("SEEDING SIMPLIFIED MENUS")
    print_info(f"Started at: {datetime.now()}")

    # Show transfer numbers from config
    print_info(f"Sales Transfer: {config.SALES_TRANSFER_NUMBER or 'NOT SET'}")
    print_info(f"Support Transfer: {config.SUPPORT_TRANSFER_NUMBER or 'NOT SET'}")

    if not config.SALES_TRANSFER_NUMBER or not config.SUPPORT_TRANSFER_NUMBER:
        print_error("Please set SALES_TRANSFER_NUMBER and SUPPORT_TRANSFER_NUMBER in .env")
        return 1

    db = SessionLocal()

    try:
        # Step 1: Delete existing menus
        print_info("Deleting existing menus...")
        db.query(MenuConfiguration).delete()
        db.commit()
        print_success("Existing menus deleted")

        # Step 2: Create simplified menus
        print_header("CREATING MENUS")

        # MAIN MENU - Simple 2 options
        print_info("Creating main_menu...")
        create_menu(
            db,
            menu_id='main_menu',
            parent_menu_id=None,
            title='Main Menu',
            message='Welcome. Press 1 for Sales, or Press 2 for Support.',
            digit_actions={
                '1': 'sales_transfer',
                '2': 'support_transfer'
            },
            action_type='menu'
        )
        print_success("main_menu created")

        # SALES TRANSFER
        print_info("Creating sales_transfer...")
        create_menu(
            db,
            menu_id='sales_transfer',
            parent_menu_id='main_menu',
            title='Sales Transfer',
            message='Connecting you to Sales. Please hold.',
            action_type='transfer',
            action_config={'transfer_number': config.SALES_TRANSFER_NUMBER}
        )
        print_success(f"sales_transfer created -> {config.SALES_TRANSFER_NUMBER}")

        # SUPPORT TRANSFER
        print_info("Creating support_transfer...")
        create_menu(
            db,
            menu_id='support_transfer',
            parent_menu_id='main_menu',
            title='Support Transfer',
            message='Connecting you to Support. Please hold.',
            action_type='transfer',
            action_config={'transfer_number': config.SUPPORT_TRANSFER_NUMBER}
        )
        print_success(f"support_transfer created -> {config.SUPPORT_TRANSFER_NUMBER}")

        # INVALID INPUT - Returns to main menu
        print_info("Creating invalid_input...")
        create_menu(
            db,
            menu_id='invalid_input',
            parent_menu_id='main_menu',
            title='Invalid Input',
            message='Invalid input. Press 1 for Sales, or Press 2 for Support.',
            digit_actions={
                '1': 'sales_transfer',
                '2': 'support_transfer'
            },
            action_type='menu'
        )
        print_success("invalid_input created")

        # Step 3: Commit to database
        print_header("COMMITTING TO DATABASE")
        print_info("Saving menus...")
        db.commit()
        print_success("All menus saved successfully")

        # Step 4: Verify
        print_header("VERIFICATION")
        menu_count = db.query(MenuConfiguration).count()
        print_success(f"Total menus in database: {menu_count}")

        # List all menus
        print_info("Menu structure:")
        all_menus = db.query(MenuConfiguration).all()
        for menu in sorted(all_menus, key=lambda m: m.menu_id):
            parent = f" (parent: {menu.parent_menu_id})" if menu.parent_menu_id else " (ROOT)"
            print(f"  - {menu.menu_id}{parent}")

        print_header("SEEDING COMPLETE")
        print_success(f"Created {menu_count} menus successfully")
        print(f"\nMenu Flow:")
        print(f"  Press 1 -> Sales ({config.SALES_TRANSFER_NUMBER})")
        print(f"  Press 2 -> Support ({config.SUPPORT_TRANSFER_NUMBER})")
        print(f"  Other   -> Invalid input, retry")
        return 0

    except Exception as e:
        print_error(f"Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 1

    finally:
        db.close()
        print_info(f"Completed at: {datetime.now()}")
        print()


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
