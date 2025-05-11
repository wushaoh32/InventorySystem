import sqlite3
from typing import List, Tuple


class DBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path, timeout=10)
        self.conn.execute("PRAGMA journal_mode=WAL")
        return self

    def execute(self, sql: str, params: Tuple = ()) -> List[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchall()
        self.conn.commit()
        return result

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()