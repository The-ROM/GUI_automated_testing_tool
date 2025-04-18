# ui/user_admin.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class UserAdminPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("用户管理功能开发中..."))
        self.setLayout(layout)
