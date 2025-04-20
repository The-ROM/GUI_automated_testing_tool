import pyautogui
import time
import threading
from pynput import keyboard
from core.db import Database
from utils.logger import log
import pytesseract
from PIL import Image
import os

class TestExecutor:
    def __init__(self, config):
        self.click_interval = config.get("click_interval", 0.1)
        self.timeout = config.get("timeout", 10)
        self.ocr_enabled = True
        self.image_retry_count = config.get("image_retry_count", 3)
        self.image_confidence = config.get("image_confidence", 0.8)
        self.enable_fallback = config.get("enable_fallback", True)
        self.paused_event = threading.Event()
        self.paused_event.set()  # 默认不暂停
        self.stopped_event = threading.Event()

        self.is_playing = False  # 控制是否处于回放状态
        self.is_recording = False  # 控制是否处于录制状态
        self.script = []  # 用于存储当前回放的脚本

    def _locate(self, locator):
        if locator["by"] == "coords":
            pt = tuple(locator["value"])

        elif locator["by"] == "image":
            image_path = locator["value"]
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图像文件不存在：{image_path}")

            pt = None
            for attempt in range(self.image_retry_count):
                pt = pyautogui.locateCenterOnScreen(image_path, confidence=self.image_confidence)
                if pt:
                    log(f"[图像识别] 成功（第 {attempt + 1} 次）")
                    break
                else:
                    log(f"[图像识别] 第 {attempt + 1} 次失败，重试中...")
                    time.sleep(0.3)
            if pt is None:
                fallback = locator.get("fallback")
                if self.enable_fallback and fallback and len(fallback) == 2:
                    log(f"[WARN] 图像识别失败，使用 fallback 坐标：{fallback}")
                    pt = tuple(fallback)
                else:
                    raise RuntimeError(f"图像未匹配到屏幕：{image_path}")

        elif locator["by"] == "text":
            if not self.ocr_enabled:
                raise ValueError("未启用 OCR 功能")
            screenshot = pyautogui.screenshot()
            boxes = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
            for i in range(len(boxes["text"])):
                if locator["value"] in boxes["text"][i]:
                    x = boxes["left"][i] + boxes["width"][i] // 2
                    y = boxes["top"][i] + boxes["height"][i] // 2
                    pt = (x, y)
                    break
            else:
                raise ValueError(f"OCR 未找到文本：{locator['value']}")
        else:
            raise ValueError(f"不支持的定位方式: {locator['by']}")

        if not isinstance(pt, (tuple, list)) or len(pt) != 2:
            raise TypeError(f"_locate 返回非法坐标：{pt}")
        return pt

    def click(self, locator):
        """模拟点击操作"""
        pt = self._locate(locator)
        if not pt:
            raise RuntimeError("定位失败")
        pyautogui.click(pt)
        time.sleep(self.click_interval)

    def move(self, locator):
        """模拟鼠标移动"""
        pt = self._locate(locator)
        if pt:
            pyautogui.moveTo(pt)
            time.sleep(0.1)

    def scroll(self, position, delta):
        """模拟滚动操作"""
        x, y = position
        pyautogui.moveTo(x, y)
        pyautogui.scroll(delta)
        time.sleep(0.1)

    def input_key(self, key):
        """模拟键盘输入"""
        pyautogui.write(key)
        time.sleep(self.click_interval)

    def assert_exists(self, locator):
        """验证元素是否存在"""
        pt = self._locate(locator)
        if not pt:
            raise AssertionError("断言失败：目标元素未出现")

    def screenshot_error(self, step, reason, index):
        """当步骤执行失败时截图"""
        os.makedirs("data/errors", exist_ok=True)
        fname = f"data/errors/step_{index}_error.png"
        pyautogui.screenshot(fname)
        log(f"[ERROR] 步骤 {index} 执行失败: {reason}，截图已保存到 {fname}")

    def run_script(self, script, script_id=None):
        """执行回放脚本"""
        log("🟢 开始执行脚本...")
        self.is_playing = True
        log_lines = []  # 用于存储每一步的执行日志
        start_time = time.time()
        last_time = None
        total = len(script)
        success = 0

        for i, step in enumerate(script):
            if self.stopped_event.is_set():
                log("回放已停止")
                break

            while not self.paused_event.is_set():
                time.sleep(0.1)

            # 同步操作时间间隔
            if last_time and "time" in step:
                delay = step["time"] - last_time
                time.sleep(delay)

            last_time = step["time"]

            # 更新实时执行状态
            log(f"正在执行第 {i+1} 步，共 {total} 步")
            try:
                # 自动补 locator
                if "locator" not in step:
                    if "position" in step:
                        step["locator"] = {"by": "coords", "value": step["position"]}
                    elif "x" in step and "y" in step:
                        step["locator"] = {"by": "coords", "value": [step["x"], step["y"]]}
                    else:
                        raise ValueError("无 locator 且无坐标信息，无法执行")

                action = step["action"]
                now = step.get("time")
                if last_time and now:
                    delay = now - last_time
                    if 0 < delay < 5:
                        time.sleep(delay)
                last_time = now

                # 处理拖动操作
                if step["action"] == "drag":
                    start_pos = step["start_position"]
                    end_pos = step["end_position"]
                    self.mouse_drag(start_pos, end_pos)  # 调用拖动操作
                elif step["action"] == "click":
                    self.click(step["locator"])
                elif step["action"] == "move":
                    self.move(step["locator"])
                elif step["action"] == "scroll":
                    self.scroll(step["locator"]["value"], step["delta"])
                elif step["action"] == "keyboard":
                    self.input_key(step["key"])
                elif step["action"] == "assert":
                    self.assert_exists(step["locator"])
                else:
                    raise ValueError(f"未知操作类型：{step['action']}")

                success += 1
                log_line = f"[✓] 步骤 {i+1}/{total} 执行成功: {action}"
                log_lines.append(log_line)
                log(log_line)
            except Exception as e:
                log_line = f"[✗] 步骤 {i + 1}/{total} 执行失败: {e}"
                log_lines.append(log_line)
                log(log_line)
                self.screenshot_error(step, str(e), i + 1)
                continue

        duration = round(time.time() - start_time, 2)
        rate = round(success / total * 100, 2) if total else 0
        log(f"✅ 执行完成：成功 {success} / 共 {total} 步，成功率 {rate}%，用时 {duration}s")

        # 保存报告到数据库
        db = Database.get_instance()
        report_detail = "\n".join(log_lines)
        db.execute("""
                   INSERT INTO reports(script_id, summary, success_rate, duration, detail)
                   VALUES (?, ?, ?, ?, ?)
                   """, (script_id, f"成功率 {rate}%", rate / 100, duration, report_detail))
        log("测试报告已生成并保存到数据库")

    def pause(self):
        """暂停回放"""
        log("暂停回放")
        self.paused_event.clear()  # 清除暂停标志

    def resume(self):
        """恢复回放"""
        log("恢复回放")
        self.paused_event.set()  # 设置为恢复状态

    def stop(self):
        """停止回放"""
        log("停止回放")
        self.stopped_event.set()  # 设置停止标志

    def on_key_press(self, key):
        """监听按键事件"""
        try:
            if key == keyboard.Key.esc:  # 按 ESC 键停止回放
                self.stop()
            elif key.char == 'p':  # 按 P 键暂停或恢复回放
                if self.paused_event.is_set():
                    self.pause()
                else:
                    self.resume()
            elif key.char == 's':  # 按 S 键停止回放
                self.stop()
        except AttributeError:
            pass  # 忽略非字符键

    def mouse_drag(self, start, end):
        """模拟鼠标拖动"""
        pyautogui.mouseDown(x=start[0], y=start[1])  # 鼠标按下
        pyautogui.moveTo(end[0], end[1], duration=0.5)  # 拖动到目标位置
        pyautogui.mouseUp()  # 鼠标松开
