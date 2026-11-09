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

_CREATE_MEMORIES_SQL = """
    CREATE TABLE {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        category TEXT NOT NULL,
        memory_key TEXT NOT NULL,
        value TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE(session_id, category, memory_key)
    )
"""


# =========================================================
# INITIALIZE MEMORY
# =========================================================

def init_memory():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='memories'"
    )
    table_exists = cursor.fetchone() is not None

    if not table_exists:
        cursor.execute(_CREATE_MEMORIES_SQL.format(table_name="memories"))
    else:
        cursor.execute("PRAGMA table_info(memories)")
        columns = {row[1] for row in cursor.fetchall()}

        if "session_id" not in columns:
            # Keep existing single-user memories under the local CLI session,
            # while moving the unique key to include the session identifier.
            cursor.execute(
                _CREATE_MEMORIES_SQL.format(table_name="memories_migrated")
            )
            cursor.execute("""
                INSERT INTO memories_migrated
                    (id, session_id, category, memory_key, value, created_at, updated_at)
                SELECT id, 'local', category, memory_key, value, created_at, updated_at
                FROM memories
            """)
            cursor.execute("DROP TABLE memories")
            cursor.execute("ALTER TABLE memories_migrated RENAME TO memories")

    conn.commit()
    conn.close()


# =========================================================
# REMEMBER
# =========================================================

def remember(category, key, value, session_id="local"):
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
        (session_id, category, memory_key, value, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)

        ON CONFLICT(session_id, category, memory_key)
        DO UPDATE SET
            value = excluded.value,
            updated_at = excluded.updated_at
    """, (
        str(session_id),
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

def recall(category=None, session_id="local"):
    """
    Returns all memories, or only one category.
    """

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    if category is None:

        cursor.execute("""
            SELECT category, memory_key, value
            FROM memories
            WHERE session_id=?
            ORDER BY category, memory_key
        """, (str(session_id),))

    else:

        cursor.execute("""
            SELECT category, memory_key, value
            FROM memories
            WHERE session_id=? AND category=?
            ORDER BY memory_key
        """, (str(session_id), category))

    rows = cursor.fetchall()

    conn.close()

    return rows


# =========================================================
# GET ONE MEMORY
# =========================================================

def get_memory(category, key, session_id="local"):
    """
    Returns one specific memory.
    """

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT value
        FROM memories
        WHERE session_id=? AND category=? AND memory_key=?
    """, (
        str(session_id),
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

def forget(category, key, session_id="local"):
    """
    Deletes one memory.
    """

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM memories
        WHERE session_id=? AND category=? AND memory_key=?
    """, (
        str(session_id),
        category,
        key,
    ))

    conn.commit()
    conn.close()
