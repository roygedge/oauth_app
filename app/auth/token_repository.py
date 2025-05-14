from contextlib import contextmanager

from app.models.token import Token
from app.database import SessionLocal


@contextmanager
def get_db_session():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    finally:
        db.close()

def commit_db():
    """Commit a database session."""
    with get_db_session() as db:
        db.commit()

def add_token_to_db(token: Token):
    """Add a token to the database.
    Args:
        token: The token to add to the database
    """
    with get_db_session() as db:
        db.add(token)

def get_last_token():
    """Get the most recent token from the database.
    
    Returns:
        The most recent token from the database or None if the token is expired
    """
    with get_db_session() as db:
        token = db.query(Token).order_by(Token.id.desc()).first()
        return token


