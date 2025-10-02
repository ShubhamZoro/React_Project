from pathlib import Path
import json
from sqlalchemy import create_engine, text, String, Integer, Float, Text, TIMESTAMP
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TSVECTOR
from config import settings
from typing import Any

file_path = Path("items.json")

class Base(DeclarativeBase):
    pass



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

    # 👇 Add this line so SQLAlchemy can see the column
    tsv: Mapped[Any] = mapped_column(TSVECTOR)

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
engine = create_engine(settings.DATABASE_URL, future=True, pool_pre_ping=True, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Setup ----------
def _postgres_setup(conn):
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
    conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS idx_items_tsv ON items USING GIN (tsv);")
    conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);")
    conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS idx_items_company ON items(company);")
    conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS idx_items_itemname ON items(item_name);")

def _seed_from_json_if_present(conn):
    if not file_path.exists():
        return
    data = json.loads(file_path.read_text(encoding="utf-8"))
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

    def norm(it):
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
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        _postgres_setup(conn)
        if seed_from_json:
            _seed_from_json_if_present(conn)
