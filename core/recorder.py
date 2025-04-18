from pynput import mouse, keyboard
import threading
import time

class Recorder:
    def __init__(self):
        self.script = []
        self.mouse_listener = None
        self.keyboard_listener = None
        self.recording = False

    def start(self):
        self.script.clear()
        self.recording = True

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

    def stop(self):
        self.recording = False
        if self.mouse_listener: self.mouse_listener.stop()
        if self.keyboard_listener: self.keyboard_listener.stop()
        return self.script

    def on_click(self, x, y, button, pressed):
        if not self.recording or not pressed:
            return
        self.script.append({
            "action": "click",
            "locator": {"by": "coords", "value": [x, y]},
            "button": str(button),
            "time": time.time()
        })

    def on_scroll(self, x, y, dx, dy):
        if not self.recording:
            return
        self.script.append({
            "action": "scroll",
            "position": [x, y],
            "delta": dy,
            "time": time.time()
        })

    def on_move(self, x, y):
        if not self.recording:
            return
        self.script.append({
            "action": "move",
            "position": [x, y],
            "time": time.time()
        })

    def on_key_press(self, key):
        if not self.recording:
            return
        try:
            key_val = key.char
        except AttributeError:
            key_val = str(key)
        self.script.append({
            "action": "keyboard",
            "key": key_val,
            "time": time.time()
        })
