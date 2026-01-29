"""
Configuration management for the IVR system.

This file centralizes all configuration settings from environment variables.
By using a config file, we can easily change settings without modifying code.

Why config.py?
- Separates configuration from code (12-factor app principle)
- Makes it easy to have different settings for dev/prod
- All settings in one place for easy reference
- Environment variables keep secrets secure
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This reads your local .env file and makes variables available via os.environ
load_dotenv()


class Config:
    """
    Configuration class that loads settings from environment variables.

    If an environment variable is not set, it uses a default value (or None).
    This allows the app to work with default settings even if .env is missing.
    """

    # ===== DATABASE CONFIGURATION =====
    # This tells SQLAlchemy how to connect to PostgreSQL
    # Format: postgresql://user:password@host:port/database
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://localhost/ivr_db'
    )

    # ===== REDIS CONFIGURATION =====
    # Redis is used for fast session storage (in-memory)
    # We store each call session here while the call is active
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    # Full Redis URL for easy connection
    REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

    # ===== PLIVO CONFIGURATION =====
    # These are your Plivo account credentials
    # Get from: https://console.plivo.com/dashboard/
    PLIVO_AUTH_ID = os.getenv('PLIVO_AUTH_ID', '')
    PLIVO_AUTH_TOKEN = os.getenv('PLIVO_AUTH_TOKEN', '')
    PLIVO_PHONE_NUMBER = os.getenv('PLIVO_PHONE_NUMBER', '')

    # ===== FLASK CONFIGURATION =====
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # ===== IVR SETTINGS =====
    # These control how the IVR system behaves

    # How long to wait for user to press a digit (seconds)
    DEFAULT_TIMEOUT = int(os.getenv('DEFAULT_TIMEOUT', 5))

    # How many times to ask for input before giving up
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))

    # How long to keep session data in Redis (seconds)
    # 1800 seconds = 30 minutes
    SESSION_TTL = int(os.getenv('SESSION_TTL', 1800))

    # How long to cache menu configurations (seconds)
    MENU_CACHE_TTL = 3600  # 1 hour

    # ===== TRANSFER NUMBERS =====
    # Phone numbers to transfer calls to
    SALES_TRANSFER_NUMBER = os.getenv('SALES_TRANSFER_NUMBER', '')
    SUPPORT_TRANSFER_NUMBER = os.getenv('SUPPORT_TRANSFER_NUMBER', '')

    # ===== WEBHOOK BASE URL =====
    # Your public URL (ngrok or production domain)
    WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL', 'http://localhost:5001')


def get_config():
    """
    Return the config object.

    This function makes it easy to get config from anywhere in the app:

        from config import get_config
        config = get_config()
        db_url = config.DATABASE_URL
    """
    return Config()


# Print config values when this file is imported (helps with debugging)
if __name__ == '__main__':
    config = get_config()
    print("=== IVR System Configuration ===")
    print(f"Database URL: {config.DATABASE_URL}")
    print(f"Redis URL: {config.REDIS_URL}")
    print(f"Plivo Phone: {config.PLIVO_PHONE_NUMBER}")
    print(f"Flask Environment: {config.FLASK_ENV}")
    print(f"Default Timeout: {config.DEFAULT_TIMEOUT}s")
    print(f"Session TTL: {config.SESSION_TTL}s")
