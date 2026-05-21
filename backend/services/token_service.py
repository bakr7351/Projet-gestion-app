import uuid
from datetime import datetime, timedelta
from backend.extensions import db
from backend.models.token import Token


def generate_token(user_id: int, token_type: str, expires_in: int) -> str:
    """Generate a unique token, store it, and return the token string."""
    token_str = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    token = Token(
        user_id=user_id,
        token=token_str,
        type=token_type,
        expires_at=expires_at,
        used=False,
    )
    db.session.add(token)
    db.session.commit()
    return token_str


def validate_token(token_str: str, token_type: str) -> Token | None:
    """Return the Token if valid (exists, correct type, not expired, not used)."""
    token = Token.query.filter_by(token=token_str, type=token_type, used=False).first()
    if not token:
        return None
    if token.expires_at < datetime.utcnow():
        return None
    return token


def invalidate_token(token_str: str) -> None:
    """Mark a single token as used."""
    token = Token.query.filter_by(token=token_str).first()
    if token:
        token.used = True
        db.session.commit()


def invalidate_all_tokens(user_id: int, token_type: str) -> None:
    """Mark all tokens of a given type for a user as used."""
    Token.query.filter_by(user_id=user_id, type=token_type, used=False).update({"used": True})
    db.session.commit()
