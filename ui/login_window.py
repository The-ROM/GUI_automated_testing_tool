# login_window.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from core.user_manager import UserManager
from ui.main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.um = UserManager()
        self.setWindowTitle("登录")
        self.user_edit = QLineEdit(); self.user_edit.setPlaceholderText("用户名")
        self.pwd_edit  = QLineEdit(); self.pwd_edit.setPlaceholderText("密码");
        self.pwd_edit.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton("登录")
        self.register_btn = QPushButton("注册账号")
        layout = QVBoxLayout()

        self.register_btn.clicked.connect(self.open_register)


        layout.addWidget(self.user_edit); layout.addWidget(self.pwd_edit); layout.addWidget(self.login_btn)
        self.setLayout(layout)
        layout.addWidget(self.register_btn)
        self.login_btn.clicked.connect(self.do_login)

    def do_login(self):
        user = self.user_edit.text().strip()
        pwd  = self.pwd_edit.text().strip()
        role = self.um.authenticate(user, pwd)
        if role:
            from utils.session import save_login
            save_login(user, role)  # ✅ 记住登录信息
            self.close()
            self.main_window = MainWindow(user, role)  # ✅ 必须持久引用
            self.main_window.show()
        else:
            QMessageBox.warning(self, "错误", "用户名或密码错误")

    def open_register(self):
        from ui.register_window import RegisterWindow
        self.reg_win = RegisterWindow()
        self.reg_win.show()
