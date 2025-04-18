import pyautogui
import time
import threading

class Recorder:
    def __init__(self):
        self.recording = False
        self.script = []

    def start(self):
        self.recording = True
        self.script.clear()
        threading.Thread(target=self._record).start()

    def stop(self):
        self.recording = False
        return self.script

    def _record(self):
        while self.recording:
            x, y = pyautogui.position()
            self.script.append({
                "action": "click",
                "x": x,
                "y": y,
                "time": time.time()
            })
            time.sleep(1)  # 简化：每秒录一次位置（可扩展为事件监听）
