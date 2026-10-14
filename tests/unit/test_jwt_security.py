from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.services import auth


@pytest.fixture(autouse=True)
def jwt_test_configuration(monkeypatch):
    monkeypatch.setattr(auth.settings, "secret_key", "local-test-signing-key-" * 3)
    monkeypatch.setattr(auth.settings, "algorithm", "HS256")


def test_current_tokens_roundtrip_and_existing_hs256_claims_remain_compatible():
    assert auth.decode_token(auth.create_access_token("user-123")) == "user-123"
    token = jwt.encode({"sub": "existing-user", "exp": int((datetime.now(UTC) + timedelta(minutes=5)).timestamp())}, auth.settings.secret_key, algorithm="HS256")
    assert auth.decode_token(token) == "existing-user"


def test_expired_tokens_are_rejected():
    token = jwt.encode({"sub": "user", "exp": datetime.now(UTC) - timedelta(seconds=5)}, auth.settings.secret_key, algorithm="HS256")
    assert auth.decode_token(token) is None


@pytest.mark.parametrize("claims", [{"sub": "user"}, {"exp": 9999999999}, {"sub": {"id": "user"}, "exp": 9999999999}])
def test_required_and_typed_claims_are_enforced(claims):
    token = jwt.encode(claims, auth.settings.secret_key, algorithm="HS256")
    assert auth.decode_token(token) is None


def test_token_cannot_choose_another_algorithm_or_unsigned_mode():
    claims = {"sub": "user", "exp": 9999999999}
    assert auth.decode_token(jwt.encode(claims, auth.settings.secret_key, algorithm="HS384")) is None
    assert auth.decode_token(jwt.encode(claims, "", algorithm="none")) is None


def test_corrupt_and_oversized_tokens_fail_closed():
    assert auth.decode_token("invalid") is None
    assert auth.decode_token("x" * 8193) is None
