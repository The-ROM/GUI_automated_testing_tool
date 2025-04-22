from pynput import mouse, keyboard
import threading
import time
import pyautogui
import os
from utils.logger import log  # 假设有日志模块

class Recorder:
    def __init__(self, config=None):
        self.script = []  # 保存所有操作的列表
        self.lock = threading.Lock()  # 用于确保线程安全
        self.mouse_listener = None
        self.keyboard_listener = None
        self.recording = False  # 录制状态
        self.is_recording = False  # 控制是否在录制状态
        self.stop_event = threading.Event()  # 停止录制的事件
        self.image_save_path = "recorded_images/"
        self.config = config or {}
        self.image_region_size = self.config.get("image_region_size", 100)  # ✅ 默认100
        self.dragging = False
        self.drag_start = None
        self.last_move = None
        os.makedirs(self.image_save_path, exist_ok=True)  # 创建图像保存目录

    def start(self):
        """开始录制并启动倒计时"""
        with self.lock:  # 线程安全
            self.script.clear()
        self.is_recording = True
        self.recording = True
        self.stop_event.clear()  # 清除停止事件标志

        # 倒计时2秒
        print("录制将在2秒后开始...")
        threading.Thread(target=self.countdown).start()  # 启动倒计时线程

        # 启动鼠标监听
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click,
            on_scroll=self.on_scroll,
            on_move=self.on_move
        )
        self.mouse_listener.start()

        # 启动键盘监听
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press
        )
        self.keyboard_listener.start()

    def countdown(self):
        """倒计时2秒"""
        for i in range(2, 0, -1):
            print(f"倒计时: {i}秒")
            time.sleep(1)
        print("开始录制...")

    def stop(self):
        """停止录制并返回脚本"""
        print("录制停止")
        self.is_recording = False
        self.recording = False
        self.stop_event.set()  # 设置停止事件标志
        if self.mouse_listener: self.mouse_listener.stop()
        if self.keyboard_listener: self.keyboard_listener.stop()
        return self.script

    def capture_image(self, region=None):
        """捕获图像并保存"""
        image_path = f"{self.image_save_path}{time.time()}.png"
        screenshot = pyautogui.screenshot(region=region) if region else pyautogui.screenshot()
        screenshot.save(image_path)
        print(f"图像已保存: {image_path}")
        return image_path

    def on_click(self, x, y, button, pressed):
        if not self.recording:
            return

        if pressed:
            self.dragging = True
            self.drag_start = (x, y)

            with self.lock:
                self.script.append({
                    "action": "mouseDown",
                    "position": [x, y],
                    "button": button.name,
                    "time": time.time()
                })

        else:
            self.dragging = False
            start = self.drag_start
            end = (x, y)
            dist = ((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5

            if dist < 10:  # 拖动距离小，认为是点击
                region = (x - self.image_region_size // 2,
                          y - self.image_region_size // 2,
                          self.image_region_size,
                          self.image_region_size)
                image_path = self.capture_image(region)

                with self.lock:
                    self.script.append({
                        "action": "click",
                        "locator": {
                            "by": "image",
                            "value": image_path,
                            "fallback": [x, y]
                        },
                        "button": button.name,
                        "time": time.time()
                    })

            if dist >= 10:  # 是拖动
                with self.lock:
                    self.script.append({
                        "action": "mouseUp",
                        "position": [x, y],
                        "button": button.name,
                        "time": time.time()
                    })

            self.drag_start = None

    def on_scroll(self, x, y, dx, dy):
        """监听鼠标滚轮"""
        if not self.recording:
            return
        with self.lock:
            self.script.append({
                "action": "scroll",
                "position": [x, y],
                "delta": dy,
                "time": time.time()
            })

    def on_move(self, x, y):
        if not self.recording or not self.dragging:
            return
        self.last_move = (x, y)
        with self.lock:
            self.script.append({
                "action": "move",
                "position": [x, y],
                "time": time.time()
            })

    def on_key_press(self, key):
        """监听键盘按键"""
        if not self.recording:
            return
        try:
            key_val = key.char
        except AttributeError:
            key_val = str(key)

        if key_val == 'esc':  # 停止录制
            self.stop()
        else:
            with self.lock:
                self.script.append({
                    "action": "keyboard",
                    "key": key_val,
                    "time": time.time()
                })

    def insert_drag_moves(self, start, end, interval=20):
        """为拖动插入平滑 move 步骤"""
        x1, y1 = start
        x2, y2 = end
        dx, dy = x2 - x1, y2 - y1
        distance = (dx ** 2 + dy ** 2) ** 0.5
        steps = max(1, int(distance // interval))

        for i in range(1, steps):
            t = i / steps
            x = int(x1 + dx * t)
            y = int(y1 + dy * t)
            self.script.append({
                "action": "move",
                "position": [x, y],
                "time": time.time()
            })
