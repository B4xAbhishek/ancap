# JWT library migration: python-jose → PyJWT

Scope: backend **access-token** encode/decode only (`app/services/auth.py`). No
changes to refresh/session storage, wallet keys, blockchain signing, encryption or
production settings.

## Wire contract and backward compatibility

- Signing algorithm: existing `ALGORITHM=HS256`, verified using the same
  `SECRET_KEY` and an explicit decoder algorithm allow-list.
- Issued claims are still `sub` (non-empty **string**) and `exp` (UTC epoch
  seconds). `ACCESS_TOKEN_EXPIRE_MINUTES` is unchanged.
- Previously issued `python-jose` HS256 tokens with a non-empty string `sub`,
  valid future `exp`, and a matching signing key are accepted until expiry.
  There is no token rotation or production key change in this PR.
- Expired, incorrectly signed, malformed, unsigned, alternate-algorithm, and
  invalid-subject tokens fail authentication. Tokens missing either `exp` or
  `sub` now fail closed because `jwt.decode` explicitly requires both claims.
  Such tokens were not issued by the existing `create_access_token`.
- PyJWT validates `sub` as a string. Any malformed legacy tokens that used
  non-string subjects will now be rejected; callers must sign in again.
  Blank subjects are rejected at issuance and decoding.
- `nbf` continues to be checked when present by the JWT library.
- No `aud`/`iss` claims are added, and the token layout is unchanged.
  Existing bearer header and HttpOnly cookie authentication consume the same
  `decode_token` interface.

## Dependency and packaging changes

- `requirements.in` and hash-locked `requirements.txt` replace
  `python-jose[cryptography]==3.3.0` with `PyJWT==2.15.1`.
- The runtime lock removes no-longer-needed transitive-only `ecdsa`, `rsa`,
  `pyasn1`, and `six`, based on the dependency annotations in the existing
  Python 3.11 lock. `cryptography` remains pinned explicitly for other
  application dependencies.
- PyJWT distribution SHA-256 hashes come from the official PyPI release files.
  The rest of the lock is untouched to minimize unrelated dependency updates.
- The runtime Docker image installs from the hash-locked `requirements.txt`;
  backend CI installs `.[dev]` using dependencies from `requirements.in`
  and also builds the Docker runtime image. Both paths must pass before merge.
- PyJWT does not accept an empty HMAC signing key. Pytest now generates a
  throwaway key when `SECRET_KEY` is unset. Production already requires a
  configured `SECRET_KEY` and is **not** assigned a new fallback.

## Verification before merge

1. `python -m pytest -q tests/test_auth_jwt_migration.py tests/test_unit.py`
2. `python -m pytest -q` with the project's PostgreSQL test environment.
3. Backend CI (including Docker image installation from the hash lock), CodeQL,
   dependency/security checks and any configured lockfile validation.
4. Staging-only authentication smoke test: sign in, use bearer/cookie tokens,
   validate a legitimately issued pre-migration token, and confirm expiry/401.
5. Confirm production `SECRET_KEY` and `ALGORITHM=HS256` remain unchanged.
   **Do not expose or copy the production secret or tokens into CI/tests.**

Only merge/deploy with separate written approval. For rollback, revert this
migration and restore the previous dependency lock; existing correctly signed
HS256 JWTs do not require re-issuance solely because of the library switch.
