from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./neurolla.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency: yields a session and guarantees it's closed
    after the request finishes, even if the handler raises. Routes
    declare `db: Session = Depends(get_db)` instead of calling
    SessionLocal() directly and leaking the connection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()