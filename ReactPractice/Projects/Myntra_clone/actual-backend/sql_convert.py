

import json
import sqlite3
from pathlib import Path

DB_PATH = "items.db"
JSON_PATH = "items.json"

# ---------- ITEMS ----------
def ensure_items_table(conn: sqlite3.Connection):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id TEXT PRIMARY KEY,
        image TEXT,
        company TEXT,
        item_name TEXT,
        original_price REAL,
        current_price REAL,
        discount_percentage INTEGER,
        return_period INTEGER,
        delivery_date TEXT,
        rating_stars REAL,
        rating_count INTEGER,
        category TEXT,
        tags TEXT
    )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_category ON items(category)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_tags ON items(tags)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_item_name ON items(item_name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_company ON items(company)")

def ensure_items_fts(conn: sqlite3.Connection):
    # Create FTS5 virtual table (fast, ranked search).
    # If your Python/SQLite build lacks FTS5, this will raise an error.
    conn.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
        id,
        item_name,
        company,
        category,
        tags,
        tokenize = 'unicode61'
    );
    """)
    # Keep FTS in sync with base table
    conn.execute("""
    CREATE TRIGGER IF NOT EXISTS items_ai
    AFTER INSERT ON items BEGIN
        INSERT INTO items_fts (id, item_name, company, category, tags)
        VALUES (new.id, new.item_name, new.company, new.category, new.tags);
    END;
    """)
    conn.execute("""
    CREATE TRIGGER IF NOT EXISTS items_ad
    AFTER DELETE ON items BEGIN
        DELETE FROM items_fts WHERE id = old.id;
    END;
    """)
    conn.execute("""
    CREATE TRIGGER IF NOT EXISTS items_au
    AFTER UPDATE ON items BEGIN
        UPDATE items_fts
        SET item_name = new.item_name,
            company   = new.company,
            category  = new.category,
            tags      = new.tags
        WHERE id = old.id;
    END;
    """)

def load_items_from_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # shape: {"items": [ [ {...}, ... ] ]}
    return data["items"][0]

def upsert_items(conn: sqlite3.Connection, items: list[dict]):
    sql = """
    INSERT INTO items (
        id, image, company, item_name,
        original_price, current_price, discount_percentage,
        return_period, delivery_date,
        rating_stars, rating_count,
        category, tags
    ) VALUES (
        ?, ?, ?, ?,
        ?, ?, ?,
        ?, ?,
        ?, ?,
        ?, ?
    )
    ON CONFLICT(id) DO UPDATE SET
        image=excluded.image,
        company=excluded.company,
        item_name=excluded.item_name,
        original_price=excluded.original_price,
        current_price=excluded.current_price,
        discount_percentage=excluded.discount_percentage,
        return_period=excluded.return_period,
        delivery_date=excluded.delivery_date,
        rating_stars=excluded.rating_stars,
        rating_count=excluded.rating_count,
        category=excluded.category,
        tags=excluded.tags
    """
    for it in items:
        conn.execute(sql, (
            it["id"],
            it.get("image"),
            it.get("company"),
            it.get("item_name"),
            it.get("original_price"),
            it.get("current_price"),
            it.get("discount_percentage"),
            it.get("return_period"),
            it.get("delivery_date"),
            (it.get("rating") or {}).get("stars"),
            (it.get("rating") or {}).get("count"),
            it.get("category"),
            it.get("tags"),
        ))

# ---------- USERS ----------
def ensure_users_table(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

# ---------- BAG ITEMS ----------
def ensure_bag_table(conn: sqlite3.Connection):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS bag_items (
      email TEXT NOT NULL,
      product_id TEXT NOT NULL,
      added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (email, product_id)
    );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_bag_email ON bag_items(email)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_bag_product ON bag_items(product_id)")

def backfill_fts(conn: sqlite3.Connection):
    # Clear and repopulate FTS from items
    conn.execute("DELETE FROM items_fts")
    conn.execute("""
        INSERT INTO items_fts (id, item_name, company, category, tags)
        SELECT id, item_name, company, category, tags
        FROM items
    """)

# ---------- MAIN ----------
def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        # create/ensure tables
        ensure_items_table(conn)
        # Try to create FTS (skip quietly if FTS not available)
        try:
            ensure_items_fts(conn)
            has_fts = True
        except sqlite3.OperationalError:
            # Your SQLite build might not include FTS5
            print("⚠️  FTS5 not available in this SQLite build. Falling back to LIKE search in API.")
            has_fts = False

        ensure_users_table(conn)
        ensure_bag_table(conn)

        # seed items from JSON if present
        seeded = False
        if Path(JSON_PATH).exists():
            items = load_items_from_json(JSON_PATH)
            upsert_items(conn, items)
            print(f"✅ Seeded {len(items)} items into {DB_PATH}")
            seeded = True
        else:
            print(f"ℹ️ {JSON_PATH} not found, skipping items seed.")

        # Backfill FTS once (on first run or after reseed)
        if has_fts:
            # Only backfill if we just seeded or if FTS is empty
            cnt = conn.execute("SELECT COUNT(1) FROM items_fts").fetchone()[0]
            if seeded or cnt == 0:
                backfill_fts(conn)
                print("✅ FTS backfilled from items")

        conn.commit()
        print("✅ users and bag_items tables ready in items.db")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
