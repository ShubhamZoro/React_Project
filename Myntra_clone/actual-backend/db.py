from __future__ import annotations
from pathlib import Path
import json
from typing import Mapping, Any

from sqlalchemy import (
    create_engine, text, String, Integer, Float, Text, TIMESTAMP
)
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from config import settings

file_path = os.path.join(os.path.dirname(__file__), 'items.json')

class Base(DeclarativeBase):
    pass

# ---------- ORM Models ----------
class Item(Base):
    __tablename__ = "items"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    image: Mapped[str | None] = mapped_column(Text, nullable=True)
    company: Mapped[str | None] = mapped_column(String(255))
    item_name: Mapped[str | None] = mapped_column(Text)
    original_price: Mapped[float | None] = mapped_column(Float)
    current_price: Mapped[float | None] = mapped_column(Float)
    discount_percentage: Mapped[int | None] = mapped_column(Integer)
    return_period: Mapped[int | None] = mapped_column(Integer)
    delivery_date: Mapped[str | None] = mapped_column(String(64))
    rating_stars: Mapped[float | None] = mapped_column(Float)
    rating_count: Mapped[int | None] = mapped_column(Integer)
    category: Mapped[str | None] = mapped_column(String(128))
    tags: Mapped[str | None] = mapped_column(Text)
    # Postgres FTS column (created in _postgres_setup)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    salt: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[Any] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

class BagItem(Base):
    __tablename__ = "bag_items"
    email: Mapped[str] = mapped_column(String(320), primary_key=True)
    product_id: Mapped[str] = mapped_column(String, primary_key=True)
    added_at: Mapped[Any] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

# ---------- Engine & Session ----------
engine = create_engine(
    settings.DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    echo=False,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Bootstrap helpers ----------
def _sqlite_setup(conn):
    # FTS5 virtual table + triggers (idempotent)
    conn.exec_driver_sql("""
    CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
        id, item_name, company, category, tags, tokenize='unicode61'
    );
    """)
    conn.exec_driver_sql("""
    CREATE TRIGGER IF NOT EXISTS items_ai
    AFTER INSERT ON items BEGIN
        INSERT INTO items_fts (id, item_name, company, category, tags)
        VALUES (new.id, new.item_name, new.company, new.category, new.tags);
    END;""")
    conn.exec_driver_sql("""
    CREATE TRIGGER IF NOT EXISTS items_ad
    AFTER DELETE ON items BEGIN
        DELETE FROM items_fts WHERE id = old.id;
    END;""")
    conn.exec_driver_sql("""
    CREATE TRIGGER IF NOT EXISTS items_au
    AFTER UPDATE ON items BEGIN
        UPDATE items_fts
        SET item_name = new.item_name, company = new.company,
            category = new.category, tags = new.tags
        WHERE id = old.id;
    END;""")

def _postgres_setup(conn):
    # Ensure tsvector column + GIN index for FTS (idempotent)
    conn.exec_driver_sql("""
    ALTER TABLE IF EXISTS items
    ADD COLUMN IF NOT EXISTS tsv tsvector
    GENERATED ALWAYS AS (
      to_tsvector('simple',
        coalesce(item_name,'') || ' ' ||
        coalesce(company,'')   || ' ' ||
        coalesce(category,'')  || ' ' ||
        coalesce(tags,'')
      )
    ) STORED;
    """)
    conn.exec_driver_sql("""CREATE INDEX IF NOT EXISTS idx_items_tsv ON items USING GIN (tsv);""")
    # Helpful regular indexes
    conn.exec_driver_sql("""CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);""")
    conn.exec_driver_sql("""CREATE INDEX IF NOT EXISTS idx_items_company  ON items(company);""")
    conn.exec_driver_sql("""CREATE INDEX IF NOT EXISTS idx_items_itemname ON items(item_name);""")

def _seed_from_json_if_present(conn):
    path = Path(JSON_PATH)
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data["items"][0]

    upsert_sql = text("""
    INSERT INTO items (id,image,company,item_name,original_price,current_price,discount_percentage,
                       return_period,delivery_date,rating_stars,rating_count,category,tags)
    VALUES (:id,:image,:company,:item_name,:original_price,:current_price,:discount_percentage,
            :return_period,:delivery_date,:rating_stars,:rating_count,:category,:tags)
    ON CONFLICT(id) DO UPDATE SET
        image=excluded.image, company=excluded.company, item_name=excluded.item_name,
        original_price=excluded.original_price, current_price=excluded.current_price,
        discount_percentage=excluded.discount_percentage, return_period=excluded.return_period,
        delivery_date=excluded.delivery_date, rating_stars=excluded.rating_stars,
        rating_count=excluded.rating_count, category=excluded.category, tags=excluded.tags
    """)

    def norm(it: Mapping[str, Any]) -> Mapping[str, Any]:
        r = it.get("rating") or {}
        return dict(
            id=it["id"], image=it.get("image"), company=it.get("company"),
            item_name=it.get("item_name"), original_price=it.get("original_price"),
            current_price=it.get("current_price"), discount_percentage=it.get("discount_percentage"),
            return_period=it.get("return_period"), delivery_date=it.get("delivery_date"),
            rating_stars=r.get("stars"), rating_count=r.get("count"),
            category=it.get("category"), tags=it.get("tags"),
        )

    for it in items:
        conn.execute(upsert_sql, norm(it))

def init_db(seed_from_json: bool = True):
    # Base tables
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        if engine.dialect.name == "sqlite":
            _sqlite_setup(conn)
        else:
            _postgres_setup(conn)
        if seed_from_json:
            _seed_from_json_if_present(conn)
