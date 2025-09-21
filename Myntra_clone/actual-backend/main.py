from typing import Literal
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, or_, and_, func, Table, MetaData, literal_column

import config
from db import init_db, get_session, Item, User, BagItem, engine
from functions import create_access_token, hash_password, verify_password, get_current_user

@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db(seed_from_json=True)  # ensure tables/FTS/seed before serving
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ALLOW_ORIGINS or ["*"],
    allow_methods=config.CORS_ALLOW_METHODS,
    allow_headers=config.CORS_ALLOW_HEADERS,
)

# ---------------- Items ----------------
@app.get("/items")
def get_items(db: Session = Depends(get_session)):
    items = db.execute(select(Item)).scalars().all()
    return {"items": [{c.name: getattr(i, c.name) for c in i.__table__.columns} for i in items]}

@app.post("/items", status_code=201)
def create_item(payload: dict, db: Session = Depends(get_session)):
    import uuid
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
    password = payload.get("password") or ""
    email = (payload.get("email") or "").strip()
    if not username or not password:
        raise HTTPException(status_code=400, detail="username and password are required")

    exists = db.scalar(select(User.id).where(or_(User.username == username, User.email == email)))
    if exists:
        raise HTTPException(status_code=409, detail="username already exists")

    pwd_hash, salt = hash_password(password)
    db.add(User(username=username, email=email, password_hash=pwd_hash, salt=salt))
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="username already exists")
    return {"message": "User created"}

@app.post("/login")
def login(payload: dict, db: Session = Depends(get_session)):
    email = (payload.get("useremail") or "").strip()
    password = payload.get("password") or ""
    if not email or not password:
        raise HTTPException(status_code=400, detail="username and password are required")

    row = db.execute(
        select(User.id, User.username, User.email, User.password_hash, User.salt).where(User.email == email)
    ).mappings().first()

    if not row or not verify_password(password, row["password_hash"], row["salt"]):
        raise HTTPException(status_code=401, detail="invalid credentials")

    token = create_access_token(str(row["id"]), extra={"username": row["username"], "email": row["email"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": row["id"], "username": row["username"], "email": row["email"]},
    }

@app.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}

# ---------------- Bag (JWT user) ----------------
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

# ---------------- Search (ORM/Core) ----------------
@app.get("/search/items")
def search_items(
    q: str = Query(..., min_length=1, description="Free text search"),
    limit: int = Query(50, ge=1, le=200, description="Max items to return"),
    mode: Literal["auto","fts","like"] = Query("auto", description="Force fts/like or auto"),
    op:   Literal["AND","OR"] = Query("AND", description="Combine words for LIKE fallback"),
    db: Session = Depends(get_session)
):
    def search_like():
        terms = [t for t in q.split() if t]
        if not terms:
            return []
        if engine.dialect.name == "sqlite":
            parts = [
                or_(
                    func.lower(Item.item_name).like(f"%{t.lower()}%"),
                    func.lower(Item.company).like(f"%{t.lower()}%"),
                    func.lower(Item.category).like(f"%{t.lower()}%"),
                    func.lower(Item.tags).like(f"%{t.lower()}%"),
                ) for t in terms
            ]
        else:
            parts = [
                or_(
                    Item.item_name.ilike(f"%{t}%"),
                    Item.company.ilike(f"%{t}%"),
                    Item.category.ilike(f"%{t}%"),
                    Item.tags.ilike(f"%{t}%"),
                ) for t in terms
            ]
        cond = and_(*parts) if op == "AND" else or_(*parts)
        rows = db.execute(select(Item).where(cond).limit(limit)).scalars().all()
        return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows]

    def search_fts():
        if engine.dialect.name == "postgresql":
            ts_query = func.plainto_tsquery("simple", q)
            rank = func.ts_rank(Item.__table__.c.tsv, ts_query)
            stmt = (
                select(Item, rank.label("rank"))
                .where(Item.__table__.c.tsv.op("@@")(ts_query))
                .order_by(func.desc("rank"))
                .limit(limit)
            )
            rows = db.execute(stmt).mappings().all()
            out = []
            for r in rows:
                i = r[Item]
                out.append({c.name: getattr(i, c.name) for c in i.__table__.columns})
            return out
        else:
            metadata = MetaData()
            items_fts = Table("items_fts", metadata)
            import re
            phrases = re.findall(r'"([^"]+)"', q)
            unquoted = re.sub(r'"[^"]+"', " ", q)
            tokens = re.findall(r"\w+", unquoted.lower())
            match_expr = " ".join([*(f'"{p.strip()}"' for p in phrases if p.strip()), *(f"{t}*" for t in tokens)]) or q

            stmt = (
                select(Item)
                .select_from(items_fts.join(Item, Item.id == literal_column("items_fts.id")))
                .where(items_fts.c.id.op("MATCH")(match_expr))
                .limit(limit)
            )
            rows = db.execute(stmt).scalars().all()
            return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows]

    if mode in ("fts", "auto"):
        return {"items": search_fts()}
    return {"items": search_like()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
