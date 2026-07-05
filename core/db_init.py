import server.models  # registers all ORM classes against Base before create_all

from server.database import Base
from server.database import engine


def init_db():
    """
    Creates every table defined in server/models.py if it does not
    already exist. Safe to call on every startup - SQLAlchemy's
    create_all is idempotent (skips tables that already exist).

    Must be the very first thing every entry-point script calls,
    before importing commander, risk_guard, journal, or analytics,
    since those modules open a SessionLocal in their __init__ methods
    and will crash with "no such table" if create_all has not run yet.
    """
    Base.metadata.create_all(
        bind=engine
    )
