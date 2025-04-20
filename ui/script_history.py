from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget, QTextEdit,
    QHBoxLayout, QMessageBox, QLineEdit
)
from core.script_manager import ScriptManager
from core.test_executor import TestExecutor
from core.config_manager import ConfigManager
import json
import threading

class ScriptHistory(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("历史脚本管理")
        self.manager = ScriptManager()
        self.executor = TestExecutor(ConfigManager().load_all())

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("输入脚本ID/标题/标签进行搜索")
        self.search_bar.textChanged.connect(self.load_scripts)
        layout.addWidget(self.search_bar)

        self.script_list = QListWidget()
        self.script_view = QTextEdit()
        self.script_view.setReadOnly(True)

        layout.addWidget(self.script_list)
        layout.addWidget(self.script_view)

        self.refresh_btn = QPushButton("刷新列表")
        self.play_btn = QPushButton("回放选中脚本")
        self.jump_btn = QPushButton("打开脚本")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.play_btn)
        btn_layout.addWidget(self.jump_btn)

        layout.addLayout(btn_layout)

        self.refresh_btn.clicked.connect(self.load_scripts)
        self.play_btn.clicked.connect(self.play_script)
        self.jump_btn.clicked.connect(self.jump_to_editor)
        self.script_list.currentItemChanged.connect(self.show_script_content)

        self.load_scripts()

    def load_scripts(self):
        keyword = self.search_bar.text().strip().lower()
        self.script_list.clear()
        self.scripts = self.manager.list_scripts()
        filtered = []
        for s in self.scripts:
            match = keyword in str(s["id"]).lower() or                     keyword in (s.get("title") or "").lower() or                     keyword in (s.get("tags") or "").lower()
            if keyword == "" or match:
                filtered.append(s)
        self.scripts = filtered
        for s in filtered:
            self.script_list.addItem(f"ID: {s['id']} | {s.get('title', '无标题')} |{s.get('tags', '无标签')}| {s['created_at']}")

    def show_script_content(self):
        index = self.script_list.currentRow()
        if index >= 0:
            sid = self.scripts[index]["id"]
            content = self.manager.load_by_id(sid)
            self.script_view.setPlainText(json.dumps(content, indent=4, ensure_ascii=False))
        else:
            self.script_view.clear()

    def play_script(self):
        index = self.script_list.currentRow()
        if index < 0:
            QMessageBox.warning(self, "未选择脚本", "请选择一个脚本再进行回放。")
            return
        sid = self.scripts[index]["id"]
        script = self.manager.load_by_id(sid)
        def _run():
            try:
                self.executor.run_script(script)
                QMessageBox.information(self, "回放完成", f"脚本 {sid} 执行完毕")
            except Exception as e:
                QMessageBox.critical(self, "回放失败", str(e))
        threading.Thread(target=_run).start()

    def jump_to_editor(self):
        index = self.script_list.currentRow()
        if index >= 0 and self.main_window:
            sid = self.scripts[index]["id"]
            self.main_window.open_script_by_id(sid)