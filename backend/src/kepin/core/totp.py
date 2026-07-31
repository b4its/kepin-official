"""TOTP (RFC 6238) and recovery-code helpers — stdlib only.

Secrets are stored as base32 strings (never logged). Recovery codes are
stored as SHA-256 hashes (JSON list in ``users.mfa_recovery_codes``).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import struct
import time

_ISSUER = "KePin"
_STEP = 30
_DIGITS = 6


def generate_base32_secret(length: int = 32) -> str:
    """Random base32 secret (default 32 chars == 160 bits)."""
    raw = secrets.token_bytes(length * 5 // 8)
    return base64.b32encode(raw).decode().rstrip("=")


def _decoded_secret(secret: str) -> bytes:
    padded = secret.upper() + "=" * ((8 - len(secret) % 8) % 8)
    return base64.b32decode(padded)


def totp_code(secret: str, for_time: int | None = None) -> str:
    """6-digit TOTP code for ``for_time`` (unix seconds) or now."""
    counter = (for_time if for_time is not None else int(time.time())) // _STEP
    msg = struct.pack(">Q", counter)
    digest = hmac.new(_decoded_secret(secret), msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    binary = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{binary % 10 ** _DIGITS:0{_DIGITS}d}"


def verify_totp(secret: str, code: str, window: int = 1) -> bool:
    """Validate ``code`` allowing ``window`` steps before/after the current one."""
    if not code or not code.isdigit() or len(code) != _DIGITS:
        return False
    now = int(time.time())
    return any(
        hmac.compare_digest(totp_code(secret, now + step * _STEP), code)
        for step in range(-window, window + 1)
    )


def otpauth_uri(secret: str, account: str, issuer: str = _ISSUER) -> str:
    """otpauth:// URI for authenticator apps (manual/QR enrolment)."""
    label = f"{issuer}:{account}"
    return (
        f"otpauth://totp/{label}?secret={secret}&issuer={issuer}"
        f"&algorithm=SHA1&digits={_DIGITS}&period={_STEP}"
    )


def generate_recovery_codes(count: int = 8) -> list[str]:
    """Plain-text recovery codes formatted ``XXXX-XXXX``."""
    codes = []
    for _ in range(count):
        token = secrets.token_hex(4).upper()
        codes.append(f"{token[:4]}-{token[4:]}")
    return codes


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def hash_recovery_codes(codes: list[str]) -> str:
    """JSON list of SHA-256 hashes for storage."""
    return json.dumps([_hash_code(c) for c in codes])


def verify_recovery_code(code: str, stored_json: str | None) -> tuple[bool, list[str]]:
    """Check ``code`` against stored hashes; returns (matched, remaining hashes).

    A successful match removes the used code from the returned list so the
    caller can persist the new list (one-time use).
    """
    if not stored_json or not code:
        return False, []
    try:
        hashes: list[str] = json.loads(stored_json)
    except (ValueError, TypeError):
        return False, []
    code_hash = _hash_code(code.strip().upper())
    if code_hash in hashes:
        remaining = [h for h in hashes if h != code_hash]
        return True, remaining
    return False, hashes
