import os
import time
from datetime import datetime, timedelta

class Logger:
    def __init__(self, log_dir="data/logs", keep_days=7):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.keep_days = keep_days
        self._cleanup_old_logs()

    def _now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _log_file_path(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"{date_str}.log")

    def _write(self, level, message):
        msg = f"[{self._now()}] [{level.upper()}] {message}"
        print(msg)  # 控制台输出
        with open(self._log_file_path(), "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    def info(self, message): self._write("INFO", message)
    def warn(self, message): self._write("WARN", message)
    def error(self, message): self._write("ERROR", message)

    def _cleanup_old_logs(self):
        now = time.time()
        for filename in os.listdir(self.log_dir):
            path = os.path.join(self.log_dir, filename)
            if os.path.isfile(path):
                modified_time = os.path.getmtime(path)
                if now - modified_time > self.keep_days * 86400:
                    os.remove(path)

# 单例全局日志实例
_logger = Logger()

def log(msg): _logger.info(msg)
def warn(msg): _logger.warn(msg)
def error(msg): _logger.error(msg)
def get_logger(): return _logger  # 如需自定义参数可改此接口
