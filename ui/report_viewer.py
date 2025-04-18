from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class ReportViewer(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("报告查看功能正在开发中..."))
        self.setLayout(layout)
