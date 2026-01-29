"""
Models package - Database table definitions.

This file makes it easy to import models from anywhere in the app.

Instead of:
    from models.call_log import CallLog
    from models.caller_history import CallerHistory
    from models.menu_config import MenuConfiguration

You can do:
    from models import CallLog, CallerHistory, MenuConfiguration
"""

from models.database import Base, SessionLocal, engine, get_db, init_db
from models.call_log import CallLog
from models.caller_history import CallerHistory
from models.menu_config import MenuConfiguration

__all__ = [
    'Base',
    'SessionLocal',
    'engine',
    'get_db',
    'init_db',
    'CallLog',
    'CallerHistory',
    'MenuConfiguration',
]
