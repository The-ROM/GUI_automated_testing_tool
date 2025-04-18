# ui/config_page.py

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class ConfigPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("系统配置功能开发中..."))
        self.setLayout(layout)
