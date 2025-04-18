# main.py
import sys
from PyQt5.QtWidgets import QApplication
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from utils.session import load_login
from core.user_manager import UserManager
from utils.logger import log

def ensure_admin():
    um = UserManager()
    try:
        um.add_user("admin", "admin123", role="admin")
        log("已创建默认管理员账号：admin/admin123")
    except ValueError:
        log("管理员账号已存在")

if __name__ == "__main__":
    log("启动 GUI 自动化测试工具...")
    ensure_admin()

    app = QApplication(sys.argv)
    # 读取记住的登录信息
    session = load_login()
    if session:
        window = MainWindow(session["username"], session["role"])
    else:
        window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
