"""Password hashing.

The only place in the project that touches a plaintext password. It is
hashed here and the plaintext is never stored, logged, or returned.
"""

from pwdlib import PasswordHash

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
