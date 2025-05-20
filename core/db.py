import sqlite3
import os

class APIKeyDB:
    def __init__(self, db_path="api_keys.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                key TEXT NOT NULL,
                UNIQUE(provider)
            )
        ''')
        self.conn.commit()

    def save_key(self, provider: str, key: str):
        self.cursor.execute(
            "INSERT OR REPLACE INTO api_keys (provider, key) VALUES (?, ?)", 
            (provider, key)
        )
        self.conn.commit()
        return True

    def get_key(self, provider: str) -> str:
        self.cursor.execute(
            "SELECT key FROM api_keys WHERE provider = ?", 
            (provider,)
        )
        row = self.cursor.fetchone()
        return row[0] if row else ""

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()