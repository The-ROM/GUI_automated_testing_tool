import sqlite3
import threading
from utils.logger import log

class Database:
    _instance = None
    _lock = threading.Lock()

    def __init__(self, path="data/app.db"):
        # 确保 data 目录存在
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)

        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
        log(f"SQLite 数据库已初始化：{path}")

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = Database()
        return cls._instance

    def _init_tables(self):
        c = self.conn.cursor()
        # 用户表
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role     TEXT NOT NULL
        )""")
        # 脚本表
        c.execute("""
        CREATE TABLE IF NOT EXISTS scripts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            content    TEXT    NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        # 配置表
        c.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )""")
        self.conn.commit()

    def execute(self, sql, params=()):
        c = self.conn.cursor()
        c.execute(sql, params)
        self.conn.commit()
        return c

    def query(self, sql, params=()):
        c = self.conn.cursor()
        c.execute(sql, params)
        return c.fetchall()
