"""Regression tests for the python-jose -> PyJWT HS256 migration.

Legacy tokens are produced using only RFC 7515 Base64URL/HMAC primitives,
independently of PyJWT, to exercise wire-format backward compatibility.
No production signing keys or live tokens are used.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.services import auth


_TEST_KEY = "jwt-migration-test-only-key-" + ("x" * 40)


@pytest.fixture(autouse=True)
def _isolated_jwt_settings(monkeypatch):
    monkeypatch.setattr(
        auth,
        "settings",
        SimpleNamespace(
            secret_key=_TEST_KEY,
            algorithm="HS256",
            access_token_expire_minutes=60,
        ),
    )


def _base64url(data: dict) -> str:
    encoded = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(encoded).rstrip(b"=").decode("ascii")


def _legacy_hmac_token(
    claims: dict, *, key: str = _TEST_KEY, algorithm: str = "HS256"
) -> str:
    """Generate a standard JOSE token without using either JWT library."""
    header = _base64url({"typ": "JWT", "alg": algorithm})
    payload = _base64url(claims)
    signing_input = f"{header}.{payload}"
    if algorithm == "none":
        return signing_input + "."
    digest = hashlib.sha256 if algorithm == "HS256" else hashlib.sha512
    signature = hmac.new(key.encode("utf-8"), signing_input.encode("ascii"), digest).digest()
    return signing_input + "." + base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")


def _exp_in(seconds: int) -> int:
    return int((datetime.now(timezone.utc) + timedelta(seconds=seconds)).timestamp())


def test_new_jwt_keeps_hs256_sub_exp_contract():
    token = auth.create_access_token("legacy-user-123")
    header_b64, payload_b64, signature = token.split(".")
    header = json.loads(base64.urlsafe_b64decode(header_b64 + "=="))
    payload = json.loads(base64.urlsafe_b64decode(payload_b64 + "=="))

    assert header["alg"] == "HS256"
    assert signature
    assert set(payload) == {"sub", "exp"}
    assert payload["sub"] == "legacy-user-123"
    assert isinstance(payload["exp"], int)
    assert payload["exp"] > _exp_in(0)
    assert auth.decode_token(token) == "legacy-user-123"


def test_legacy_python_jose_wire_format_token_remains_valid():
    old_format_token = _legacy_hmac_token({"sub": "existing-account", "exp": _exp_in(3600)})
    assert auth.decode_token(old_format_token) == "existing-account"


@pytest.mark.parametrize("claims", [
    {"sub": "expired-account", "exp": 1},
    {"sub": "missing-exp"},
    {"exp": _exp_in(3600)},
    {"sub": "bad-exp", "exp": "not-a-timestamp"},
    {"sub": "not-yet-valid", "exp": _exp_in(3600), "nbf": _exp_in(1800)},
])
def test_expiration_required_claims_and_time_constraints_are_validated(claims):
    assert auth.decode_token(_legacy_hmac_token(claims)) is None


@pytest.mark.parametrize("sub", [None, 123, True, {"id": "unexpected"}, ["user"], ""])
def test_invalid_subject_types_or_empty_subject_rejected(sub):
    token = _legacy_hmac_token({"sub": sub, "exp": _exp_in(3600)})
    assert auth.decode_token(token) is None


@pytest.mark.parametrize("subject", [None, 123, "", False])
def test_issuer_rejects_invalid_subject(subject):
    with pytest.raises(ValueError, match="JWT subject must be a non-empty string"):
        auth.create_access_token(subject)


@pytest.mark.parametrize("algorithm", ["HS512", "none"])
def test_rejects_alternate_and_unsigned_algorithms(algorithm):
    token = _legacy_hmac_token(
        {"sub": "user-123", "exp": _exp_in(3600)}, algorithm=algorithm
    )
    assert auth.decode_token(token) is None


def test_signature_and_jwt_structure_are_verified():
    claims = {"sub": "user-123", "exp": _exp_in(3600)}
    wrong_key = _legacy_hmac_token(claims, key="a-different-hmac-key-" + ("y" * 40))
    assert auth.decode_token(wrong_key) is None
    assert auth.decode_token("not-a-jwt") is None
    assert auth.decode_token("") is None


def test_valid_legacy_token_expires_without_grace_period():
    token = _legacy_hmac_token({"sub": "old-user", "exp": _exp_in(-10)})
    assert auth.decode_token(token) is None
