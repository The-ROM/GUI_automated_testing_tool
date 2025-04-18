import pyautogui, time
from utils.logger import log

class TestExecutor:
    def __init__(self, config):
        self.click_interval = config.get("click_interval", 0.5)
        self.timeout = config.get("timeout", 10)

    def _locate(self, locator):
        """
        locator = {"by":"image","value":"btn.png"}
                or {"by":"text","value":"Submit"}
        """
        if locator["by"] == "image":
            return pyautogui.locateCenterOnScreen(locator["value"], timeout=self.timeout)
        elif locator["by"] == "text":
            # 简化：文本定位可以集成OCR
            raise NotImplementedError("文本定位尚未实现")
        else:
            raise ValueError("不支持的定位方式")

    def click(self, locator):
        pt = self._locate(locator)
        if not pt:
            log(f"元素未找到：{locator}")
            raise RuntimeError("定位失败")
        pyautogui.click(pt)
        time.sleep(self.click_interval)

    def input_text(self, locator, text):
        self.click(locator)
        pyautogui.write(text, interval=0.05)

    def assert_exists(self, locator):
        pt = self._locate(locator)
        if not pt:
            log(f"断言失败：元素不存在 {locator}")
            raise AssertionError("断言失败")

    def run_script(self, script):
        """
        脚本格式示例：
        [
          {"action":"click", "locator":{"by":"image","value":"btn.png"}},
          {"action":"input", "locator":{"by":"image","value":"input.png"}, "text":"hello"},
          {"action":"assert", "locator":{"by":"image","value":"success.png"}}
        ]
        """
        for step in script:
            try:
                act = step["action"]
                if act == "click":
                    self.click(step["locator"])
                elif act == "input":
                    self.input_text(step["locator"], step["text"])
                elif act == "assert":
                    self.assert_exists(step["locator"])
                else:
                    log(f"未知动作：{act}")
                log(f"执行成功：{step}")
            except Exception as e:
                log(f"执行异常：{step} -> {e}")
                raise
