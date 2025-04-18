# ui/script_editor.py

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class ScriptEditor(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.setWindowTitle("脚本编辑器")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("脚本编辑功能开发中..."))
        self.setLayout(layout)
