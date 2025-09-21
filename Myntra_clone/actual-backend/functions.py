from __future__ import annotations
import hashlib, secrets, hmac, base64, json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from config import settings
from db import User, get_session

# ---------- Password hashing ----------
def hash_password(password: str, salt_hex: str | None = None) -> tuple[str, str]:
    salt = bytes.fromhex(salt_hex) if salt_hex else secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, settings.PBKDF2_ITERATIONS)
    return dk.hex(), salt.hex()

def verify_password(password: str, stored_hash_hex: str, salt_hex: str) -> bool:
    calc, _ = hash_password(password, salt_hex)
    return secrets.compare_digest(calc, stored_hash_hex)

# ---------- Minimal JWT (HS256) ----------
def _b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")

def create_access_token(sub: str, extra: Dict[str, Any] | None = None) -> str:
    header = {"alg": settings.ALGORITHM, "typ": "JWT"}
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }
    if extra:
        payload.update(extra)
    head = _b64url(json.dumps(header, separators=(",", ":")).encode())
    body = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(settings.SECRET_KEY.encode(), f"{head}.{body}".encode(), hashlib.sha256).digest()
    return f"{head}.{body}.{_b64url(sig)}"

def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode()
        sig = base64.urlsafe_b64decode(sig_b64 + "==")
        expected = hmac.new(settings.SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected):
            raise ValueError("bad signature")
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + "==").decode())
        if int(payload["exp"]) < int(datetime.now(timezone.utc).timestamp()):
            raise ValueError("expired")
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")

    row = db.execute(
        select(User.id, User.username, User.email).where(User.id == user_id)
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=401, detail="user not found")
    return {"id": row["id"], "username": row["username"], "email": row["email"]}
