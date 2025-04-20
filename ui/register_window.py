# ui/register_window.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from core.user_manager import UserManager

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.um = UserManager()
        self.setWindowTitle("注册账号")

        self.user_edit = QLineEdit(); self.user_edit.setPlaceholderText("用户名")
        self.pwd_edit  = QLineEdit(); self.pwd_edit.setPlaceholderText("密码"); self.pwd_edit.setEchoMode(QLineEdit.Password)
        self.confirm_edit = QLineEdit(); self.confirm_edit.setPlaceholderText("确认密码"); self.confirm_edit.setEchoMode(QLineEdit.Password)
        self.email_edit = QLineEdit(); self.email_edit.setPlaceholderText("邮箱")

        self.reg_btn = QPushButton("注册")

        layout = QVBoxLayout()
        layout.addWidget(self.user_edit)
        layout.addWidget(self.pwd_edit)
        layout.addWidget(self.confirm_edit)
        layout.addWidget(self.email_edit)
        layout.addWidget(self.reg_btn)
        self.setLayout(layout)

        self.reg_btn.clicked.connect(self.do_register)

    def do_register(self):
        user = self.user_edit.text().strip()
        pwd  = self.pwd_edit.text().strip()
        confirm = self.confirm_edit.text().strip()
        email = self.email_edit.text().strip()

        if not user or not pwd or not confirm:
            QMessageBox.warning(self, "错误", "请填写完整信息")
            return
        if pwd != confirm:
            QMessageBox.warning(self, "错误", "两次输入的密码不一致")
            return

        try:
            self.um.add_user(user, pwd, role="user", email=email)
            QMessageBox.information(self, "注册成功", "注册成功，请登录")
            self.close()
        except ValueError as e:
            QMessageBox.warning(self, "注册失败", str(e))
