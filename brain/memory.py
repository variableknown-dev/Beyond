import sqlite3
from datetime import datetime
from pathlib import Path


# =========================================================
# DATABASE
# =========================================================

DATA_DIR = Path("data")

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

DB_NAME = DATA_DIR / "memory.db"


# =========================================================
# INITIALIZE MEMORY
# =========================================================

def init_memory():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            memory_key TEXT NOT NULL,
            value TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(category, memory_key)
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# REMEMBER
# =========================================================

def remember(category, key, value):
    """
    Creates or updates a memory.
    """

    now = datetime.now().isoformat(
        timespec="seconds"
    )

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO memories
        (category, memory_key, value, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)

        ON CONFLICT(category, memory_key)
        DO UPDATE SET
            value = excluded.value,
            updated_at = excluded.updated_at
    """, (
        category,
        key,
        value,
        now,
        now,
    ))

    conn.commit()
    conn.close()


# =========================================================
# RECALL
# =========================================================

def recall(category=None):
    """
    Returns all memories, or only one category.
    """

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    if category is None:

        cursor.execute("""
            SELECT category, memory_key, value
            FROM memories
            ORDER BY category, memory_key
        """)

    else:

        cursor.execute("""
            SELECT category, memory_key, value
            FROM memories
            WHERE category=?
            ORDER BY memory_key
        """, (category,))

    rows = cursor.fetchall()

    conn.close()

    return rows


# =========================================================
# GET ONE MEMORY
# =========================================================

def get_memory(category, key):
    """
    Returns one specific memory.
    """

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT value
        FROM memories
        WHERE category=? AND memory_key=?
    """, (
        category,
        key,
    ))

    row = cursor.fetchone()

    conn.close()

    if row:
        return row[0]

    return None


# =========================================================
# FORGET
# =========================================================

def forget(category, key):
    """
    Deletes one memory.
    """

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM memories
        WHERE category=? AND memory_key=?
    """, (
        category,
        key,
    ))

    conn.commit()
    conn.close()
