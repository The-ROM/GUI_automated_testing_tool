import hashlib
from core.db import Database

class UserManager:
    def __init__(self):
        self.db = Database.get_instance()

    def _hash(self, pwd):
        return hashlib.sha256(pwd.encode("utf-8")).hexdigest()

    def add_user(self, username, password, role="tester"):
        hashed = self._hash(password)
        try:
            self.db.execute(
                "INSERT INTO users(username,password,role) VALUES (?, ?, ?)",
                (username, hashed, role)
            )
        except Exception as e:
            raise ValueError("用户已存在或插入失败") from e

    def remove_user(self, username):
        self.db.execute("DELETE FROM users WHERE username=?", (username,))

    def authenticate(self, username, password):
        hashed = self._hash(password)
        rows = self.db.query(
            "SELECT role FROM users WHERE username=? AND password=?",
            (username, hashed)
        )
        return rows[0]["role"] if rows else None

    def list_users(self):
        rows = self.db.query("SELECT username,role FROM users")
        return [dict(r) for r in rows]
