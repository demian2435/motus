"""Persistence layer base (estendibile)."""

import sqlite3
from typing import Any


class Persistence:
    def __init__(self, db_path: str = "motus.db") -> None:
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self) -> None:
        c = self.conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            rule TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()

    def save_decision(self, event: Any, rule: Any) -> None:
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO decisions (event, rule) VALUES (?, ?)",
            (str(event), str(rule)),
        )
        self.conn.commit()
