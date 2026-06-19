from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "icaro_v2.sqlite3"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


@contextmanager
def connect(db_path: Path | str = DB_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=MEMORY")
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.execute("PRAGMA synchronous=OFF")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: Path | str = DB_PATH) -> None:
    with connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS baskets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                basket_code TEXT,
                title TEXT NOT NULL,
                central_object TEXT NOT NULL,
                category TEXT,
                contracting_context TEXT,
                status TEXT NOT NULL DEFAULT 'draft',
                version INTEGER NOT NULL DEFAULT 1,
                history_json TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        ensure_column(conn, "baskets", "basket_code", "TEXT")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS basket_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                basket_id INTEGER NOT NULL,
                lot_group TEXT,
                description TEXT NOT NULL,
                unit TEXT NOT NULL,
                quantity REAL NOT NULL DEFAULT 1,
                catmat_catser TEXT,
                keywords_json TEXT NOT NULL DEFAULT '[]',
                classifications_json TEXT NOT NULL DEFAULT '[]',
                technical_notes TEXT,
                search_history_json TEXT NOT NULL DEFAULT '[]',
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(basket_id) REFERENCES baskets(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS item_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                basket_id INTEGER NOT NULL,
                basket_item_id INTEGER NOT NULL,
                source_type TEXT NOT NULL,
                origin TEXT NOT NULL,
                url TEXT NOT NULL,
                source_date TEXT,
                access_date TEXT NOT NULL,
                organization TEXT NOT NULL,
                modality TEXT,
                process_number TEXT,
                supplier TEXT,
                contracting_context TEXT NOT NULL,
                raw_payload_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY(basket_id) REFERENCES baskets(id),
                FOREIGN KEY(basket_item_id) REFERENCES basket_items(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS source_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_source_id INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL,
                quantity REAL NOT NULL DEFAULT 1,
                unit TEXT NOT NULL,
                accepted INTEGER NOT NULL DEFAULT 1,
                discard_reason TEXT,
                outlier INTEGER NOT NULL DEFAULT 0,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(item_source_id) REFERENCES item_sources(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS calculation_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                basket_id INTEGER NOT NULL,
                basket_item_id INTEGER,
                scope TEXT NOT NULL,
                mean REAL,
                median REAL,
                min_price REAL,
                max_price REAL,
                deviation REAL,
                source_count INTEGER NOT NULL DEFAULT 0,
                accepted_count INTEGER NOT NULL DEFAULT 0,
                outliers_json TEXT NOT NULL DEFAULT '[]',
                methodology TEXT NOT NULL,
                payload_json TEXT NOT NULL DEFAULT '{}',
                generated_at TEXT NOT NULL,
                FOREIGN KEY(basket_id) REFERENCES baskets(id),
                FOREIGN KEY(basket_item_id) REFERENCES basket_items(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS search_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                basket_id INTEGER NOT NULL,
                basket_item_id INTEGER,
                source_type TEXT NOT NULL,
                query TEXT NOT NULL,
                normalized_query TEXT NOT NULL,
                status TEXT NOT NULL,
                results_count INTEGER NOT NULL DEFAULT 0,
                error TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(basket_id) REFERENCES baskets(id),
                FOREIGN KEY(basket_item_id) REFERENCES basket_items(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS normalization_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT NOT NULL,
                replacement TEXT NOT NULL,
                category TEXT,
                active INTEGER NOT NULL DEFAULT 1,
                notes TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS source_validations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_source_id INTEGER NOT NULL,
                validation_type TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(item_source_id) REFERENCES item_sources(id)
            )
        """)


def ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row else None


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def json_loads(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default
