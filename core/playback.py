import threading
import time
from pynput import keyboard
from core.test_executor import TestExecutor
from utils.logger import log

class PlaybackManager:
    def __init__(self):
        self.executor = TestExecutor(config={"timeout": 10})
        self.is_paused = False  # 初始化暂停标志
        self.is_stopped = False  # 初始化停止标志
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()  # 启动键盘监听

    def on_key_press(self, key):
        """监听键盘事件"""
        try:
            if key == keyboard.Key.esc:
                self.stop_script()  # 按下 ESC 停止回放
            elif key.char == 'p':
                self.toggle_pause()  # 按下 P 键暂停/恢复回放
            elif key.char == 's':
                self.stop_script()  # 按下 S 键停止回放
        except AttributeError:
            pass  # 忽略非字符键

    def toggle_pause(self):
        """暂停或恢复脚本"""
        if self.is_paused:
            log("恢复回放")
            self.is_paused = False
        else:
            log("暂停回放")
            self.is_paused = True

    def stop_script(self):
        """停止回放"""
        log("停止回放")
        self.is_stopped = True

    def play_script(self, script):
        """开始回放脚本"""
        threading.Thread(target=self._run_script, args=(script,)).start()

    def _run_script(self, script):
        """执行回放逻辑"""
        if not script:
            log("未找到任何脚本，无法回放")
            return

        for i, step in enumerate(script):
            if self.is_stopped:
                log("回放已停止")
                break

            while self.is_paused:  # 如果处于暂停状态，等待直到恢复
                time.sleep(0.1)

            try:
                action = step["action"]
                if action == "click":
                    self.executor.click(step["locator"])
                elif action == "move":
                    self.executor.move(step["locator"])
                elif action == "scroll":
                    self.executor.scroll(step["locator"]["value"], step["delta"])
                elif action == "keyboard":
                    self.executor.input_key(step["key"])
                elif action == "assert":
                    self.executor.assert_exists(step["locator"])
                else:
                    raise ValueError(f"未知操作类型：{action}")
                log(f"[✓] 步骤 {i + 1} 执行成功")
            except Exception as e:
                log(f"[✗] 步骤 {i + 1} 执行失败: {e}")
                continue
