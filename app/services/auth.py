from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from jwt import InvalidTokenError

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
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> str | None:
    if not isinstance(token, str) or len(token) > 8192:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm], options={"require": ["exp", "sub"]})
        return payload.get("sub")
    except InvalidTokenError:
        return None
