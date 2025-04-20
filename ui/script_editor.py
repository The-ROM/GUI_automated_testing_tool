from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QLineEdit, QFileDialog, QMessageBox, QHBoxLayout
)
import json

class ScriptEditor(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager  # 脚本管理器，用于保存/导入/导出脚本
        self.script = []        # 当前编辑中的脚本

        self.setWindowTitle("脚本编辑")

        # 脚本标题输入框
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("请输入脚本名称")

        # 标签输入框（关键词，用空格或逗号分隔）
        self.tag_edit = QLineEdit()
        self.tag_edit.setPlaceholderText("请输入标签（用空格或逗号分隔）")

        # 脚本 JSON 编辑框
        self.text_edit = QTextEdit()

        # 功能按钮
        self.load_btn = QPushButton("导入脚本")       # 从文件加载
        self.save_btn = QPushButton("保存到数据库")   # 保存到数据库
        self.export_btn = QPushButton("导出为JSON")   # 导出为本地文件

        # 布局组织
        layout = QVBoxLayout()
        layout.addWidget(QLabel("脚本名称："))
        layout.addWidget(self.title_edit)

        layout.addWidget(QLabel("脚本标签："))
        layout.addWidget(self.tag_edit)

        layout.addWidget(QLabel("脚本内容（JSON）："))
        layout.addWidget(self.text_edit)

        # 按钮一行布局
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.load_btn)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.export_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)

        # 绑定按钮功能
        self.load_btn.clicked.connect(self.import_script)
        self.save_btn.clicked.connect(self.save_script)
        self.export_btn.clicked.connect(self.export_script)

    def import_script(self):
        """从 JSON 或 Python 文件导入脚本"""
        path, _ = QFileDialog.getOpenFileName(self, "选择脚本文件", "", "JSON 文件 (*.json);;Python 文件 (*.py)")
        if path:
            try:
                script = self.manager.import_from_file(path)
                self.script = script
                self.text_edit.setPlainText(json.dumps(script, indent=4, ensure_ascii=False))
                self.title_edit.setText("从文件导入的脚本")
                self.tag_edit.setText("")
            except Exception as e:
                QMessageBox.critical(self, "导入失败", str(e))

    def save_script(self):
        """保存脚本到数据库，附带标题与标签"""
        try:
            text = self.text_edit.toPlainText()
            script = json.loads(text)  # 确保 JSON 格式合法

            title = self.title_edit.text().strip() or "未命名脚本"
            tags = self.tag_edit.text().strip()

            # 判断脚本是否已有 id（即判断是否是已有脚本）
            if self.script_id is not None:
                # 如果已有 id，则更新已有脚本
                self.manager.update(self.script_id, script, title, tags)
                QMessageBox.information(self, "更新成功", f"脚本 [{title}] 已更新")
            else:
                # 如果没有 id，则保存为新脚本
                self.manager.save(script, title, tags)
                QMessageBox.information(self, "保存成功", f"脚本 [{title}] 已保存")

        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"格式错误或保存失败：{e}")

    def export_script(self):
        """导出当前脚本为 .json 文件"""
        try:
            text = self.text_edit.toPlainText()
            script = json.loads(text)
            path, _ = QFileDialog.getSaveFileName(self, "保存为 JSON 文件", "", "JSON 文件 (*.json)")
            if path:
                self.manager.export_to_file(script, path)
                QMessageBox.information(self, "导出成功", f"脚本已导出到：\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"{e}")

    def load_by_id(self, script_id):
        """供外部调用：加载指定脚本ID"""
        try:
            script = self.manager.load_by_id(script_id)
            self.script_id = script_id
            self.script = script
            self.text_edit.setPlainText(json.dumps(script, indent=4, ensure_ascii=False))
            # 如果脚本表中已存 title/tags
            self.title_edit.setText(script['title'])
            self.tag_edit.setText(script['tags'])
        except Exception as e:
            QMessageBox.critical(self, "加载失败", str(e))
