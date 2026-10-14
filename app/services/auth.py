from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

from app.config import get_settings

settings = get_settings()

# bcrypt limit is 72 bytes
MAX_BCRYPT_BYTES = 72


def _to_bcrypt_bytes(password: str) -> bytes:
    b = password.encode("utf-8")
    return b[:MAX_BCRYPT_BYTES] if len(b) > MAX_BCRYPT_BYTES else b


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_to_bcrypt_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(_to_bcrypt_bytes(plain), hashed.encode("utf-8"))


def create_access_token(subject: str) -> str:
    if not isinstance(subject, str) or not subject:
        raise ValueError("JWT subject must be a non-empty string")
    # Keep the existing sub/exp claims and configured HS256 signing key.
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub"], "verify_exp": True, "verify_sub": True},
        )
    except InvalidTokenError:
        return None
    subject = payload.get("sub")
    return subject if isinstance(subject, str) and subject else None
