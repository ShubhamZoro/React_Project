import sqlite3, hashlib, secrets, jwt, re
from datetime import datetime, timedelta, timezone
from typing import Literal, Tuple, List, Dict, Any
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import config

# ---------- DB ----------
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------- Auth / Security ----------
security = HTTPBearer()

def create_access_token(sub: str, minutes: int = config.ACCESS_TOKEN_EXPIRE_MINUTES, extra: dict | None = None) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload = {"sub": sub, "exp": exp}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)

def hash_password(password: str, salt_hex: str | None = None) -> Tuple[str, str]:
    salt = bytes.fromhex(salt_hex) if salt_hex else secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, config.PBKDF2_ITERATIONS)
    return dk.hex(), salt.hex()

def verify_password(password: str, stored_hash_hex: str, salt_hex: str) -> bool:
    calc_hash, _ = hash_password(password, salt_hex)
    return secrets.compare_digest(calc_hash, stored_hash_hex)

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = creds.credentials
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="invalid token")

    conn = get_conn()
    row = conn.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="user not found")
    return {"id": row["id"], "username": row["username"], "email": row["email"]}

# ---------- Search helpers ----------
def like_query(term: str) -> str:
    escaped = term.replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"

def fts_prefix_query(q: str) -> str:
    """
    Convert free text into an FTS5 prefix MATCH string.
    Supports quoted phrases: `"running shoes" nike` -> "\"running shoes\" nike*"
    """
    phrases = re.findall(r'"([^"]+)"', q)
    unquoted = re.sub(r'"[^"]+"', " ", q)
    tokens = re.findall(r"\w+", unquoted.lower())

    parts: List[str] = []
    for p in phrases:
        p = p.strip()
        if p:
            parts.append(f'"{p}"')   # exact phrase
    for t in tokens:
        parts.append(f"{t}*")       # prefix term
    return " ".join(parts)

def fts_available(conn: sqlite3.Connection) -> bool:
    try:
        conn.execute("SELECT 1 FROM items_fts LIMIT 1")
        return True
    except sqlite3.Error:
        return False

# ---------- Search queries ----------
def search_items_fts(conn: sqlite3.Connection, q: str, limit: int) -> List[Dict[str, Any]]:
    match = fts_prefix_query(q)
    if not match:
        return []
    rows = conn.execute(
        """
        SELECT i.*
        FROM items_fts
        JOIN items i ON i.id = items_fts.id
        WHERE items_fts MATCH ?
        ORDER BY bm25(items_fts, 0.1, 1.6, 1.3, 0.7, 0.8)  -- id,item_name,company,category,tags
        LIMIT ?
        """,
        (match, limit)
    ).fetchall()
    return [dict(r) for r in rows]

def search_items_like(conn: sqlite3.Connection, q: str, limit: int, op: Literal["AND","OR"] = "AND") -> List[Dict[str, Any]]:
    terms = [t.strip() for t in q.split() if t.strip()]
    if not terms:
        return []
    block = """
      (item_name LIKE ? ESCAPE '\\'
       OR company   LIKE ? ESCAPE '\\'
       OR category  LIKE ? ESCAPE '\\'
       OR tags      LIKE ? ESCAPE '\\')
    """
    joiner = " AND " if op == "AND" else " OR "
    where_blocks, params = [], []
    for t in terms:
        pat = like_query(t)
        where_blocks.append(block)
        params.extend([pat, pat, pat, pat])

    sql = f"""
        SELECT *
        FROM items
        WHERE {joiner.join(where_blocks)}
        LIMIT ?
    """
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]

