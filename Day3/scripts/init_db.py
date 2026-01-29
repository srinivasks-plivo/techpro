"""
Initialize Database - Create all tables in PostgreSQL

WHAT THIS DOES:
================
This script creates all database tables in PostgreSQL.

It uses SQLAlchemy to:
1. Connect to PostgreSQL
2. Create all tables defined in models
3. Verify tables were created
4. Report status

WHY RUN THIS:
=============
Before using the IVR system, you need empty tables ready to receive data.

This is a one-time setup step.

HOW TO RUN:
===========
python scripts/init_db.py
"""

import sys
from datetime import datetime

# Add parent directory to path so we can import models
sys.path.insert(0, '/Users/intern-srinivas/Desktop/TECHPRO/Day3')

from models.database import init_db, engine, Base
from models import CallLog, CallerHistory, MenuConfiguration
from sqlalchemy import inspect

def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_success(text):
    """Print success message."""
    print(f"✓ {text}")

def print_error(text):
    """Print error message."""
    print(f"✗ {text}")

def print_info(text):
    """Print info message."""
    print(f"→ {text}")

def main():
    """
    Main function to initialize database.

    Steps:
    1. Connect to database
    2. Create tables
    3. Verify tables exist
    4. List table information
    5. Report status
    """

    print_header("DATABASE INITIALIZATION")
    print_info(f"Started at: {datetime.now()}")

    try:
        # Step 1: Connect to database
        print_info("Connecting to PostgreSQL...")
        connection = engine.connect()
        print_success("Database connection established")

        # Step 2: Create tables
        print_info("Creating tables...")

        # This calls init_db() which creates all tables
        init_db()
        print_success("Tables created successfully")

        # Step 3: Verify tables exist
        print_info("Verifying tables...")

        # Get inspector to check tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        expected_tables = ['call_logs', 'caller_history', 'menu_configurations']

        for table_name in expected_tables:
            if table_name in existing_tables:
                print_success(f"Table '{table_name}' exists")
            else:
                print_error(f"Table '{table_name}' NOT found!")

        # Step 4: List table information
        print_header("TABLE DETAILS")

        for table_name in expected_tables:
            if table_name in existing_tables:
                columns = inspector.get_columns(table_name)
                print(f"\n📊 Table: {table_name}")
                print(f"   Columns: {len(columns)}")
                for col in columns:
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    print(f"     - {col['name']}: {col['type']} ({nullable})")

        # Step 5: Report status
        print_header("INITIALIZATION COMPLETE")

        all_exist = all(table in existing_tables for table in expected_tables)

        if all_exist:
            print_success(f"All {len(expected_tables)} tables created successfully")
            print(f"\nYour database is ready to use!")
            print(f"Next: python scripts/seed_menus.py (to add default menus)")
            return 0
        else:
            print_error("Some tables failed to create")
            return 1

    except Exception as e:
        print_error(f"Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        print_info(f"Completed at: {datetime.now()}")
        print()


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
