import json
from core.db import Database

class ConfigManager:
    def __init__(self):
        self.db = Database.get_instance()
        # 初始化默认配置
        defaults = {
            "click_interval": 0.5,
            "timeout": 10,
            "log_retention_days": 7,
            "report_format": "html"
        }
        for k, v in defaults.items():
            # 插入或忽略已存在的默认值
            self.db.execute(
                "INSERT OR IGNORE INTO config(key,value) VALUES (?, ?)",
                (k, json.dumps(v))
            )

    def load_all(self):
        rows = self.db.query("SELECT key,value FROM config")
        return {r["key"]: json.loads(r["value"]) for r in rows}

    def get(self, key, default=None):
        rows = self.db.query("SELECT value FROM config WHERE key=?", (key,))
        return json.loads(rows[0]["value"]) if rows else default

    def set(self, key, value):
        self.db.execute(
            "REPLACE INTO config(key,value) VALUES (?,?)",
            (key, json.dumps(value))
        )
