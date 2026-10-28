"""Password hashing and access tokens.

The only place in the project that touches a plaintext password or the JWT
signing secret.
"""

from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError

# recommended() is Argon2id with sensible cost settings. Argon2 won the
# Password Hashing Competition and is deliberately slow and memory-hungry,
# so guessing passwords from a stolen database is expensive. A general
# purpose hash like SHA-256 is far too fast for this job.
_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Turn a plaintext password into a hash safe to store."""
    # The result carries the algorithm, parameters and a random salt, so two
    # people with the same password still get different hashes.
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Check a plaintext password against a stored hash."""
    # Compares in constant time, so the duration of the check does not
    # reveal how much of the password was correct.
    return _hasher.verify(password, password_hash)


def create_access_token(user_id: int) -> str:
    """Make a signed token that identifies one user.

    The payload is signed, NOT encrypted. Anyone holding the token can read
    its contents, so it carries only the user id and the timestamps - never
    an email, a name, or anything else worth keeping private.
    """
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        # "sub" is the subject: who the token is about. It must be a string.
        "sub": str(user_id),
        # Issued at, and expires at. PyJWT checks "exp" when decoding.
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret.get_secret_value(), settings.jwt_algorithm)


def decode_access_token(token: str) -> int:
    """Return the user id in a valid token, or raise.

    Every failure - bad signature, expired, malformed, missing subject -
    raises the same error. The caller turns that into a 401.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            # A list we choose, never the algorithm named inside the token.
            # Trusting the token's own "alg" header is the classic JWT flaw:
            # an attacker sets it to "none" and the signature stops being
            # checked at all.
            algorithms=[settings.jwt_algorithm],
        )
        return int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise AuthenticationError("Invalid or expired token") from exc
