import json
import os

CONFIG_PATH = "config.json"

class ConfigManager:
    def __init__(self):
        self.config = {
            "click_interval": 0.5,
            "timeout": 10,
            "image_confidence": 0.8,
            "enable_fallback": True
        }

        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
            except Exception as e:
                print(f"[ConfigManager] 加载配置失败: {e}")

    def load_all(self):
        return self.config
