"""
Verify Setup - Test all system connections and configurations

WHAT THIS DOES:
================
Tests that everything is configured correctly:
- PostgreSQL connection
- Redis connection
- Plivo credentials
- Environment variables
- Required tables exist
- Menus are loaded

WHY RUN THIS:
=============
Before starting the Flask app, make sure everything works.

This prevents runtime errors by catching config issues early.

HOW TO RUN:

===========
python scripts/verify_setup.py
"""

import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, '/Users/intern-srinivas/Desktop/TECHPRO/Day3')

from config import get_config
from models.database import SessionLocal, engine
from models import MenuConfiguration
from services.redis_service import redis_service
from sqlalchemy import text, inspect

class Verify:
    """Verification utility."""

    def __init__(self):
        """Initialize."""
        self.checks_passed = 0
        self.checks_failed = 0
        self.config = get_config()

    def print_header(self, text):
        """Print formatted header."""
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}\n")

    def check_pass(self, text, detail=""):
        """Print passing check."""
        self.checks_passed += 1
        print(f"✓ {text}")
        if detail:
            print(f"  → {detail}")

    def check_fail(self, text, detail=""):
        """Print failing check."""
        self.checks_failed += 1
        print(f"✗ {text}")
        if detail:
            print(f"  → {detail}")

    def check_info(self, text):
        """Print info."""
        print(f"→ {text}")

    def run_all(self):
        """Run all verification checks."""

        self.print_header("SYSTEM VERIFICATION")
        self.check_info(f"Started at: {datetime.now()}")

        self.check_config()
        self.check_database()
        self.check_redis()
        self.check_plivo()
        self.check_menus()

        self.print_header("VERIFICATION SUMMARY")
        print(f"✓ Passed: {self.checks_passed}")
        print(f"✗ Failed: {self.checks_failed}")

        if self.checks_failed == 0:
            print("\n🎉 All checks passed! System is ready.")
            print("\nNext steps:")
            print("1. Start Redis: redis-cli ping")
            print("2. Start PostgreSQL: psql -l")
            print("3. Run Flask app: python app.py")
            print("4. Call your Plivo number to test")
            return 0
        else:
            print("\n⚠️  Some checks failed. Fix issues above before continuing.")
            return 1

    def check_config(self):
        """Check configuration."""
        self.print_header("CONFIGURATION")

        # Check environment variables
        self.check_info("Environment variables:")
        print(f"  FLASK_ENV: {self.config.FLASK_ENV}")
        print(f"  FLASK_DEBUG: {self.config.FLASK_DEBUG}")

        # Database URL (mask password)
        db_url = self.config.DATABASE_URL
        if 'password' in db_url:
            db_url = db_url.replace(db_url.split(':')[2].split('@')[0], '***')
        print(f"  DATABASE_URL: {db_url}")

        print(f"  REDIS_URL: {self.config.REDIS_URL}")
        print(f"  PLIVO_PHONE: {self.config.PLIVO_PHONE_NUMBER}")

        # Check timeouts and settings
        print(f"\nIVR Settings:")
        print(f"  Default timeout: {self.config.DEFAULT_TIMEOUT}s")
        print(f"  Max retries: {self.config.MAX_RETRIES}")
        print(f"  Session TTL: {self.config.SESSION_TTL}s")

        self.check_pass("Configuration loaded")

    def check_database(self):
        """Check database connection and tables."""
        self.print_header("DATABASE")

        try:
            # Test connection
            self.check_info("Testing connection...")
            connection = engine.connect()
            connection.execute(text("SELECT 1"))
            connection.close()
            self.check_pass("PostgreSQL connection successful")

            # Check tables exist
            self.check_info("Checking tables...")
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()

            expected_tables = ['call_logs', 'caller_history', 'menu_configurations']

            for table_name in expected_tables:
                if table_name in existing_tables:
                    columns = len(inspector.get_columns(table_name))
                    self.check_pass(f"Table '{table_name}' exists", f"{columns} columns")
                else:
                    self.check_fail(f"Table '{table_name}' NOT found")
                    self.check_info("Run: python scripts/init_db.py")

        except Exception as e:
            self.check_fail("Database connection failed", str(e))
            self.check_info("Make sure PostgreSQL is running")
            self.check_info("Run: brew services start postgresql@15")

    def check_redis(self):
        """Check Redis connection."""
        self.print_header("REDIS")

        try:
            self.check_info("Testing connection...")
            if redis_service.ping():
                self.check_pass("Redis connection successful")

                # Get info
                info = redis_service.redis_client.info()
                redis_version = info.get('redis_version', 'Unknown')
                used_memory = info.get('used_memory_human', 'Unknown')

                self.check_pass("Redis info retrieved", f"v{redis_version}, {used_memory} used")

            else:
                self.check_fail("Redis not responding")

        except Exception as e:
            self.check_fail("Redis connection failed", str(e))
            self.check_info("Make sure Redis is running")
            self.check_info("Run: brew services start redis")

    def check_plivo(self):
        """Check Plivo configuration."""
        self.print_header("PLIVO")

        try:
            # Check credentials exist
            auth_id = self.config.PLIVO_AUTH_ID
            auth_token = self.config.PLIVO_AUTH_TOKEN
            phone_number = self.config.PLIVO_PHONE_NUMBER

            if not auth_id or auth_id == 'your_auth_id_here':
                self.check_fail("PLIVO_AUTH_ID not configured", "Set in .env file")
            else:
                self.check_pass("PLIVO_AUTH_ID configured")

            if not auth_token or auth_token == 'your_auth_token_here':
                self.check_fail("PLIVO_AUTH_TOKEN not configured", "Set in .env file")
            else:
                self.check_pass("PLIVO_AUTH_TOKEN configured")

            if not phone_number or phone_number == '+15551234567':
                self.check_fail("PLIVO_PHONE_NUMBER not configured", "Set in .env file")
            else:
                self.check_pass("PLIVO_PHONE_NUMBER configured", phone_number)

            # Note: We can't actually test Plivo API without making requests
            self.check_info("Plivo API test requires valid credentials and network")

        except Exception as e:
            self.check_fail("Error checking Plivo config", str(e))

    def check_menus(self):
        """Check that menus are loaded."""
        self.print_header("MENUS")

        try:
            db = SessionLocal()

            # Check menus exist
            menu_count = db.query(MenuConfiguration).count()

            if menu_count == 0:
                self.check_fail("No menus found in database")
                self.check_info("Run: python scripts/seed_menus.py")
            else:
                self.check_pass(f"Menus loaded", f"{menu_count} menus found")

                # Check main_menu exists
                main_menu = db.query(MenuConfiguration).filter_by(
                    menu_id='main_menu'
                ).first()

                if main_menu:
                    self.check_pass("main_menu found", main_menu.message[:50])
                else:
                    self.check_fail("main_menu NOT found")

                # List menu structure
                self.check_info("Menu structure:")
                all_menus = db.query(MenuConfiguration).all()
                root_menus = [m for m in all_menus if m.parent_menu_id is None]
                sub_menus = [m for m in all_menus if m.parent_menu_id is not None]

                print(f"\n  Root menus ({len(root_menus)}):")
                for menu in root_menus:
                    print(f"    - {menu.menu_id}")

                print(f"\n  Sub-menus ({len(sub_menus)}):")
                for menu in sorted(sub_menus, key=lambda m: m.parent_menu_id or ''):
                    print(f"    - {menu.menu_id} (parent: {menu.parent_menu_id})")

            db.close()

        except Exception as e:
            self.check_fail("Error checking menus", str(e))
            import traceback
            traceback.print_exc()


def main():
    """Main function."""
    verify = Verify()
    exit_code = verify.run_all()

    print()
    return exit_code


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
