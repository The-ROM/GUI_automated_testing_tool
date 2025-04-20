import json
from core.db import Database

class ScriptManager:
    def __init__(self):
        self.db = Database.get_instance()

    def save(self, script, title="未命名脚本", tags=""):
        content = json.dumps(script, ensure_ascii=False)
        self.db.execute(
            "INSERT INTO scripts(title, tags, content) VALUES (?, ?, ?)",
            (title, tags, content)
        )

    def update(self, script_id, script, title, tags):
        """更新已有脚本"""
        try:
            self.db.execute("""
                            UPDATE scripts
                            SET content = ?,
                                title   = ?,
                                tags    = ?
                            WHERE id = ?
                            """, (json.dumps(script), title, tags, script_id))
            from utils.logger import log
            log(f"脚本 [{title}] 更新成功")
        except Exception as e:
            log(f"更新脚本失败: {e}")

    def load_latest(self):
        # 查询最新脚本的 id 和 content
        rows = self.db.query("SELECT id, content FROM scripts ORDER BY id DESC LIMIT 1")
        if rows:
            # 返回脚本的 id 和内容
            return {
                'script_id': rows[0]['id'],
                'content': json.loads(rows[0]['content'])
            }
        return {'script_id': None, 'content': []}

    def load_by_id(self, script_id):
        rows = self.db.query("SELECT title, tags, content FROM scripts WHERE id=?", (script_id,))
        if rows:
            # 返回脚本的 id 和内容
            return {
                'title': rows[0]['title'],
                'tags': rows[0]['tags'],
                'content': json.loads(rows[0]['content'])
            }
        return {'content': []}

    def list_scripts(self):
        rows = self.db.query("SELECT id, title, tags,created_at FROM scripts ORDER BY id DESC")
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
