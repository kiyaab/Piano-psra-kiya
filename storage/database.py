"""
KIYA Piano Studio Pro - SQLite Database Manager
Provides structured storage for user presets, favorites, practice statistics, and sessions.
"""

import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

class DatabaseManager:
    """Manages local SQLite database operations."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            app_data = os.environ.get("APPDATA")
            if app_data:
                db_dir = Path(app_data) / "KIYA_Piano_Studio_Pro"
            else:
                db_dir = Path.home() / ".kiya_piano_studio_pro"
            db_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = db_dir / "studio_data.db"

        self._init_tables()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        """Create database tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Favorites table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favorite_voices (
                    program INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Practice history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS practice_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    exercise_type TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    attempts INTEGER NOT NULL,
                    best_streak INTEGER NOT NULL,
                    duration_seconds REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Saved songs metadata
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saved_songs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    tempo REAL,
                    duration REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def record_practice_session(self, exercise_type: str, score: int, attempts: int, streak: int, duration_sec: float):
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO practice_sessions (exercise_type, score, attempts, best_streak, duration_seconds)
                VALUES (?, ?, ?, ?, ?)
            """, (exercise_type, score, attempts, streak, duration_sec))
            conn.commit()

    def get_practice_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT exercise_type, score, attempts, best_streak, duration_seconds, created_at
                FROM practice_sessions ORDER BY id DESC LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
