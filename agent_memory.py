import sqlite3
import time
import os

class AgentMemory:
    def __init__(self, db_path="agent_state.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS memory_traces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    step INTEGER,
                    state_data TEXT,
                    timestamp REAL
                )
            ''')
            conn.commit()

    def save_trace(self, step: int, state_data: str, max_retries=5):
        delay = 0.05
        for attempt in range(max_retries):
            try:
                with self._get_connection() as conn:
                    conn.execute(
                        "INSERT INTO memory_traces (step, state_data, timestamp) VALUES (?, ?, ?)",
                        (step, state_data, time.time())
                    )
                    conn.commit()
                return True
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                else:
                    raise e
        return False

    def get_traces(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT step, state_data, timestamp FROM memory_traces ORDER BY step ASC")
            return cursor.fetchall()
