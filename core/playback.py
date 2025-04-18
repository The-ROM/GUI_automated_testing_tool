import threading
import time
import json
from core.db import Database
from core.script_manager import ScriptManager
from core.test_executor import TestExecutor
from utils.logger import log

class PlaybackManager:
    def __init__(self):
        self.executor = TestExecutor(config={"timeout": 10})

    def play_latest_script(self):
        """
        回放最新的脚本。
        """
        script_manager = ScriptManager()
        script = script_manager.load_latest()
        if not script:
            log("未找到任何脚本，无法回放")
            return

        threading.Thread(target=self.executor.run_script, args=(script,)).start()

    def play_script_by_id(self, script_id):
        """
        根据 ID 回放指定脚本。
        :param script_id: 脚本 ID
        """
        script_manager = ScriptManager()
        script = script_manager.load_by_id(script_id)
        if not script:
            log(f"未找到 ID 为 {script_id} 的脚本")
            return

        threading.Thread(target=self.executor.run_script, args=(script,)).start()