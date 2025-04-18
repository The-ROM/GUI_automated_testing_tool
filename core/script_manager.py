import json
from core.db import Database

class ScriptManager:
    def __init__(self):
        self.db = Database.get_instance()

    def save(self, script):
        content = json.dumps(script, ensure_ascii=False)
        self.db.execute("INSERT INTO scripts(content) VALUES (?)", (content,))

    def load_latest(self):
        rows = self.db.query("SELECT content FROM scripts ORDER BY id DESC LIMIT 1")
        return json.loads(rows[0]["content"]) if rows else []

    def load_by_id(self, script_id):
        rows = self.db.query("SELECT content FROM scripts WHERE id=?", (script_id,))
        return json.loads(rows[0]["content"]) if rows else []

    def list_scripts(self):
        rows = self.db.query("SELECT id, created_at FROM scripts ORDER BY id DESC")
        return [dict(r) for r in rows]

    def import_from_file(self, filepath):
        if filepath.endswith(".json"):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        elif filepath.endswith(".py"):
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return [{"action": "python", "code": line.strip()} for line in lines if line.strip()]
        else:
            raise ValueError("仅支持 JSON 或 Python 文件")

    def export_to_file(self, script, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(script, f, indent=4, ensure_ascii=False)
