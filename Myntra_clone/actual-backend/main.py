from typing import Literal
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, or_, func
import uuid

import config
from db import get_session, Item, User, BagItem, setup_tables_and_indexes
from functions import create_access_token, hash_password, verify_password, get_current_user

# ---------------- App ----------------
app = FastAPI()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ALLOW_ORIGINS or ["*"],
    allow_methods=config.CORS_ALLOW_METHODS,
    allow_headers=config.CORS_ALLOW_HEADERS,
)

# ---------------- Ensure tables & indexes exist ----------------
setup_tables_and_indexes()  # Safe to run on every cold start

# ---------------- Items ----------------
@app.get("/items")
def get_items(db: Session = Depends(get_session)):
    items = db.execute(select(Item)).scalars().all()
    return {"items": [{c.name: getattr(i, c.name) for c in i.__table__.columns} for i in items]}

@app.post("/items", status_code=201)
def create_item(payload: dict, db: Session = Depends(get_session)):
    obj = Item(
        id=str(uuid.uuid4()),
        image=payload.get("image"),
        company=payload.get("company"),
        item_name=payload.get("item_name"),
        original_price=payload.get("original_price"),
        current_price=payload.get("current_price"),
        discount_percentage=payload.get("discount_percentage"),
        return_period=payload.get("return_period"),
        delivery_date=payload.get("delivery_date"),
        rating_stars=payload.get("rating_stars"),
        rating_count=payload.get("rating_count"),
        category=payload.get("category"),
        tags=payload.get("tags"),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"message": "Stored new item.", "item": {c.name: getattr(obj, c.name) for c in obj.__table__.columns}}

@app.patch("/items/{item_id}")
def update_item(item_id: str, payload: dict, db: Session = Depends(get_session)):
    stmt = (
        update(Item)
        .where(Item.id == item_id)
        .values(**{k: v for k, v in payload.items() if hasattr(Item, k)})
        .execution_options(synchronize_session="fetch")
    )
    res = db.execute(stmt)
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="item not found")
    db.commit()
    obj = db.get(Item, item_id)
    return {"item": {c.name: getattr(obj, c.name) for c in obj.__table__.columns}}

@app.delete("/items/{item_id}")
def delete_item(item_id: str, db: Session = Depends(get_session)):
    res = db.execute(delete(Item).where(Item.id == item_id))
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="item not found")
    db.commit()
    return {"ok": True}

# ---------------- Auth ----------------
@app.post("/register", status_code=201)
def register(payload: dict, db: Session = Depends(get_session)):
    username = (payload.get("username") or "").strip()
    password = (payload.get("password") or "")
    email = (payload.get("email") or "").strip()

    if not username or not password or not email:
        raise HTTPException(status_code=400, detail="username, email and password are required")

    exists = db.scalar(select(User.id).where(or_(User.username == username, User.email == email)))
    if exists:
        raise HTTPException(status_code=409, detail="username or email already exists")

    pwd_hash, salt = hash_password(password)
    user = User(username=username, email=email, password_hash=pwd_hash, salt=salt)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="error creating user")

    return {"message": "User created", "user": {"id": user.id, "username": user.username, "email": user.email}}

@app.post("/login")
def login(payload: dict, db: Session = Depends(get_session)):
    email = (payload.get("useremail") or "").strip()
    password = payload.get("password") or ""

    if not email or not password:
        raise HTTPException(status_code=400, detail="email and password are required")

    row = db.execute(
        select(User.id, User.username, User.email, User.password_hash, User.salt).where(User.email == email)
    ).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="user not found")

    if not verify_password(password, row["password_hash"], row["salt"]):
        raise HTTPException(status_code=401, detail="password does not match")

    token = create_access_token(str(row["id"]), extra={"username": row["username"], "email": row["email"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": row["id"], "username": row["username"], "email": row["email"]},
    }

@app.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}

# ---------------- Bag ----------------
@app.post("/bag", status_code=201)
def add_to_bag(payload: dict, current_user: dict = Depends(get_current_user), db: Session = Depends(get_session)):
    product_id = (payload.get("product_id") or "").strip()
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")
    email = current_user["email"]

    existing = db.get(BagItem, {"email": email, "product_id": product_id})
    if not existing:
        db.add(BagItem(email=email, product_id=product_id))
        db.commit()
    return {"ok": True, "product_id": product_id}

@app.delete("/bag/{product_id}")
def remove_from_bag(product_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_session)):
    email = current_user["email"]
    res = db.execute(delete(BagItem).where(BagItem.email == email, BagItem.product_id == product_id))
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="not found")
    db.commit()
    return {"ok": True}

@app.get("/bag/ids")
def get_bag_ids(current_user: dict = Depends(get_current_user), db: Session = Depends(get_session)):
    email = current_user["email"]
    ids = db.execute(select(BagItem.product_id).where(BagItem.email == email)).scalars().all()
    return {"ids": ids}

# ---------------- Search ----------------
@app.get("/search/items")
def search_items(
    q: str = Query(..., min_length=1, description="Free text search"),
    limit: int = Query(50, ge=1, le=200, description="Max items to return"),
    db: Session = Depends(get_session)
):
    ts_query = func.plainto_tsquery("simple", q)
    stmt = select(Item).where(Item.__table__.c.tsv.op("@@")(ts_query)).limit(limit)
    rows = db.execute(stmt).scalars().all()
    return {"items": [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows]}


# ---------------- Run ----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
