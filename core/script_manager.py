import json
from core.db import Database

class ScriptManager:
    def __init__(self):
        self.db = Database.get_instance()

    def save(self, script):
        # 脚本以 JSON 字符串形式存储
        content = json.dumps(script, ensure_ascii=False)
        self.db.execute(
            "INSERT INTO scripts(content) VALUES (?)",
            (content,)
        )

    def load_latest(self):
        rows = self.db.query(
            "SELECT content FROM scripts ORDER BY id DESC LIMIT 1"
        )
        if not rows:
            return []
        return json.loads(rows[0]["content"])

    def list_scripts(self):
        rows = self.db.query(
            "SELECT id,created_at FROM scripts ORDER BY id DESC"
        )
        return [dict(r) for r in rows]

    def load_by_id(self, script_id):
        rows = self.db.query(
            "SELECT content FROM scripts WHERE id=?",
            (script_id,)
        )
        return json.loads(rows[0]["content"]) if rows else []
