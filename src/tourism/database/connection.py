import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "git.db"
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"

def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def initialize_database():
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Не найден файл схемы БД: {SCHEMA_PATH}")
    with get_connection() as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
