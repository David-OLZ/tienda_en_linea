"""Conexión y esquema de SQLite."""
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY,
    sku         TEXT    NOT NULL UNIQUE,
    name        TEXT    NOT NULL,
    description TEXT    NOT NULL,
    price_cents INTEGER NOT NULL CHECK (price_cents > 0),
    stock       INTEGER NOT NULL CHECK (stock >= 0),
    emoji       TEXT    NOT NULL DEFAULT '📦',
    category_id INTEGER NOT NULL REFERENCES categories(id)
);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE TABLE IF NOT EXISTS carts (
    id            TEXT PRIMARY KEY,
    customer_json TEXT,
    created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS cart_items (
    cart_id    TEXT    NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (cart_id, product_id)
);
"""


def connect(path=":memory:"):
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn):
    conn.executescript(SCHEMA)
    conn.commit()
