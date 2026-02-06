"""Persistence layer base (extensible)."""

import sqlite3


class Persistence:
    """SQLite-backed persistence helper for decisions."""

    def __init__(self, db_path: str = "motus.db") -> None:
        """Initialize the database connection and schema."""
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT,
                rule TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
        )
        self.conn.commit()

    def save_decision(self, event: object, rule: object) -> None:
        """Persist a decision for auditing purposes."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO decisions (event, rule) VALUES (?, ?)",
            (str(event), str(rule)),
        )
        self.conn.commit()
