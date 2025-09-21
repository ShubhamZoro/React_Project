# main.py — FastAPI + Auth + Bag + Search (returns full items)
from typing import Literal
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware

import config
from functions import (
    get_conn, create_access_token, hash_password, verify_password,
    get_current_user, fts_available,
    search_items_fts, search_items_like
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ALLOW_ORIGINS,
    allow_methods=config.CORS_ALLOW_METHODS,
    allow_headers=config.CORS_ALLOW_HEADERS,
)

# ---------------- Items ----------------
@app.get("/items")
async def get_items():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM items").fetchall()
    conn.close()
    return {"items": [dict(r) for r in rows]}

# IF Needed
@app.post("/items", status_code=201)
async def create_item(item: dict):
    import uuid
    item_id = str(uuid.uuid4())
    item["id"] = item_id
    conn = get_conn()
    conn.execute(
        """INSERT INTO items 
        (id, image, company, item_name, original_price, current_price, discount_percentage,
         return_period, delivery_date, rating_stars, rating_count, category, tags)
        VALUES (:id, :image, :company, :item_name, :original_price, :current_price, 
                :discount_percentage, :return_period, :delivery_date, :rating_stars, 
                :rating_count, :category, :tags)""",
        item,
    )
    conn.commit()
    conn.close()
    return {"message": "Stored new item.", "item": item}

# ---------------- Auth ----------------
@app.post("/register", status_code=201)
async def register(payload: dict):
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    email = (payload.get("email") or "").strip()
    if not username or not password:
        raise HTTPException(status_code=400, detail="username and password are required")

    pwd_hash, salt = hash_password(password)
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, salt, email) VALUES (?, ?, ?, ?)",
            (username, pwd_hash, salt, email),
        )
        conn.commit()
    except Exception as e:
        # unique constraints can raise sqlite3.IntegrityError, but keep it generic
        raise HTTPException(status_code=409, detail="username already exists")
    finally:
        conn.close()
    return {"message": "User created"}

@app.post("/login")
async def login(payload: dict):
    email = (payload.get("useremail") or "").strip()
    password = payload.get("password") or ""
    if not email or not password:
        raise HTTPException(status_code=400, detail="username and password are required")

    conn = get_conn()
    row = conn.execute(
        "SELECT id, username, email, password_hash, salt FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    conn.close()
    if not row or not verify_password(password, row["password_hash"], row["salt"]):
        raise HTTPException(status_code=401, detail="invalid credentials")

    token = create_access_token(str(row["id"]), extra={"username": row["username"], "email": row["email"]})
    return {"access_token": token, "token_type": "bearer",
            "user": {"id": row["id"], "username": row["username"], "email": row["email"]}}

@app.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}

# ---------------- Bag ----------------
@app.post("/bag", status_code=201)
async def add_to_bag(payload: dict, current=Depends(get_current_user)):
    product_id = (payload.get("product_id") or "").strip()
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")
    conn = get_conn()
    try:
        conn.execute("INSERT OR IGNORE INTO bag_items (email, product_id) VALUES (?, ?)",
                     (current["email"], product_id))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "product_id": product_id}

@app.delete("/bag/{product_id}")
async def remove_from_bag(product_id: str, current=Depends(get_current_user)):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM bag_items WHERE email = ? AND product_id = ?",
                     (current["email"], product_id))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

@app.get("/bag/ids")
async def get_bag_ids(current=Depends(get_current_user)):
    conn = get_conn()
    try:
        rows = conn.execute("SELECT product_id FROM bag_items WHERE email = ?",
                            (current["email"],)).fetchall()
    finally:
        conn.close()
    return {"ids": [r["product_id"] for r in rows]}

# ---------------- Search (FULL ITEMS) ----------------
@app.get("/search/items")
async def search_items(
    q: str = Query(..., min_length=1, description="Free text search"),
    limit: int = Query(50, ge=1, le=200, description="Max items to return"),
    mode: Literal["auto","fts","like"] = Query("auto", description="Force fts/like or auto"),
    op:   Literal["AND","OR"] = Query("AND", description="Combine words for LIKE fallback"),
):
    conn = get_conn()
    try:
        fts_ok = fts_available(conn)
        if mode == "fts" or (mode == "auto" and fts_ok):
            if not fts_ok:
                raise HTTPException(status_code=503, detail="FTS not available in this SQLite build")
            items = search_items_fts(conn, q, limit)
            return {"items": items}

        items = search_items_like(conn, q, limit, op=op)
        return {"items": items}
    finally:
        conn.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)



