import hashlib
from core.db import Database

class UserManager:
    def __init__(self):
        self.db = Database.get_instance()

    def _hash(self, pwd):
        return hashlib.sha256(pwd.encode("utf-8")).hexdigest()

    def add_user(self, username, password, role="user", email=None):
        db = Database.get_instance()
        exists = db.query("SELECT 1 FROM users WHERE username=?", (username,))
        if exists:
            raise ValueError("该账号已被注册")
        db.execute("INSERT INTO users(username, password, role, email) VALUES (?, ?, ?, ?)",
                   (username, password, role, email))

    def remove_user(self, username):
        self.db.execute("DELETE FROM users WHERE username=?", (username,))

    def authenticate(self, username, password):
        hashed = self._hash(password)
        rows = self.db.query(
            "SELECT role FROM users WHERE username=? AND password=?",
            (username, password)
        )
        return rows[0]["role"] if rows else None

    def list_users(self):
        return Database.get_instance().query("SELECT * FROM users ORDER BY user_id")

    def delete_user(self, user_id):
        Database.get_instance().execute("DELETE FROM users WHERE user_id=?", (user_id,))

    def update_user_role(self, user_id, role):
        Database.get_instance().execute("UPDATE users SET role=? WHERE user_id=?", (role, user_id))

