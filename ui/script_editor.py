from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QLineEdit, QFileDialog, QMessageBox, QHBoxLayout,
    QListWidget, QSplitter, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QPixmap
from PyQt5.QtWidgets import QMenu, QAction
import json
import os
from utils.logger import log

class ScriptEditor(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.script = []
        self.script_id = None

        self.setWindowTitle("脚本编辑")

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("请输入脚本名称")

        self.tag_edit = QLineEdit()
        self.tag_edit.setPlaceholderText("请输入标签（用空格或逗号分隔）")

        self.text_edit = QTextEdit()

        self.image_list = QListWidget()
        self.image_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.image_list.itemClicked.connect(self.highlight_image_reference)

        self.image_preview = QLabel("图像预览")
        self.image_preview.setFixedHeight(150)
        self.image_preview.setStyleSheet("border: 1px solid gray; background-color: white;")
        self.image_preview.setScaledContents(True)
        self.image_list.itemClicked.connect(self.update_image_preview)
        self.image_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image_list.customContextMenuRequested.connect(self.show_image_context_menu)
        self.load_btn = QPushButton("导入脚本")
        self.save_btn = QPushButton("保存到数据库")
        self.export_btn = QPushButton("导出为JSON")

        layout = QVBoxLayout()

        name_tag_row = QHBoxLayout()
        name_tag_row.addWidget(QLabel("脚本名称："))
        name_tag_row.addWidget(self.title_edit)
        name_tag_row.addWidget(QLabel("标签："))
        name_tag_row.addWidget(self.tag_edit)
        layout.addLayout(name_tag_row)

        label_row = QHBoxLayout()
        label_row.addWidget(QLabel("脚本内容（JSON）和图像引用："))
        layout.addLayout(label_row)

        splitter = QSplitter()
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        splitter.addWidget(self.text_edit)

        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)
        right_layout.addWidget(self.image_list)
        right_layout.addWidget(self.image_preview)
        right_panel.setLayout(right_layout)

        splitter.addWidget(right_panel)

        layout.addWidget(splitter, stretch=1)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.load_btn)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.export_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)

        self.load_btn.clicked.connect(self.import_script)
        self.save_btn.clicked.connect(self.save_script)
        self.export_btn.clicked.connect(self.export_script)

    def import_script(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择脚本文件", "", "JSON 文件 (*.json);;Python 文件 (*.py)")
        if path:
            try:
                script_data = self.manager.import_from_file(path)
                self.script = script_data if isinstance(script_data, list) else script_data.get("content", [])
                self.script_id = None
                self.text_edit.setPlainText(json.dumps(self.script, indent=4, ensure_ascii=False))
                self.title_edit.setText("从文件导入的脚本")
                self.tag_edit.setText("")
                self.update_image_list(self.script)
            except Exception as e:
                QMessageBox.critical(self, "导入失败", str(e))

    def save_script(self):
        try:
            text = self.text_edit.toPlainText()
            script = json.loads(text)
            title = self.title_edit.text().strip() or "未命名脚本"
            tags = self.tag_edit.text().strip()

            if self.script_id is not None:
                self.manager.update(self.script_id, script, title, tags)
                QMessageBox.information(self, "更新成功", f"脚本 [{title}] 已更新")
            else:
                self.manager.save(script, title, tags)
                QMessageBox.information(self, "保存成功", f"脚本 [{title}] 已保存")

        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"格式错误或保存失败：{e}")

    def export_script(self):
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
        try:
            data = self.manager.load_by_id(script_id)
            self.script_id = script_id
            self.script = data.get("content", [])
            self.text_edit.setPlainText(json.dumps(self.script, indent=4, ensure_ascii=False))
            self.title_edit.setText(data.get("title", f"脚本ID：{script_id}"))
            self.tag_edit.setText(data.get("tags", ""))
            self.update_image_list(self.script)
        except Exception as e:
            QMessageBox.critical(self, "加载失败", str(e))
            log(e)

    def update_image_list(self, script):
        self.image_list.clear()
        images = self.find_images_in_script(script)
        for img in sorted(images):
            self.image_list.addItem(img)
        self.image_preview.clear()

    def find_images_in_script(self, script):
        images = set()
        try:
            if isinstance(script, list):
                for step in script:
                    if not isinstance(step, dict):
                        continue
                    # 只处理含 locator 且类型为 image 的操作
                    if "locator" in step:
                        locator = step["locator"]
                        try:
                            if locator["by"] == "image" and "value" in locator:
                                path = locator["value"]
                                if isinstance(path, str) and path:
                                    images.add(os.path.basename(path))
                        except Exception as e:
                            log(f"[图像提取异常] 步骤处理失败：{e}")
        except Exception as e:
            log(f"[图像提取失败] {e}")
        return images

    def highlight_image_reference(self, item):
        image_name = item.text()
        script_text = self.text_edit.toPlainText()
        lines = script_text.splitlines()

        for i, line in enumerate(lines):
            if image_name in line:
                cursor = self.text_edit.textCursor()
                cursor.movePosition(QTextCursor.Start)
                for _ in range(i):
                    cursor.movePosition(QTextCursor.Down)
                self.text_edit.setTextCursor(cursor)
                self.text_edit.setFocus()
                break

    def update_image_preview(self, item):
        image_name = item.text()
        full_path = os.path.join("recorded_images", image_name)
        if os.path.exists(full_path):
            pixmap = QPixmap(full_path)
            self.image_preview.setPixmap(pixmap)
        else:
            self.image_preview.setText("图像不存在")

    def show_image_context_menu(self, position):
        item = self.image_list.itemAt(position)
        if not item:
            return
        old_image_name = item.text()  # 获取当前图像的文件名

        # 创建右键菜单
        menu = QMenu()
        replace_action = QAction(f"替换图像: {old_image_name}", self)
        replace_action.triggered.connect(lambda: self.replace_image(old_image_name))  # 传递文件名给替换方法
        menu.addAction(replace_action)

        menu.exec_(self.image_list.viewport().mapToGlobal(position))


    def is_valid_image_format(self, file_path):
        """检查图像文件格式是否有效"""
        valid_extensions = [".png", ".jpg", ".jpeg"]
        _, ext = os.path.splitext(file_path)
        return ext.lower() in valid_extensions

    def replace_image(self, old_image_name):
        """替换图像并更新脚本内容"""
        new_image_path, _ = QFileDialog.getOpenFileName(self, "选择新图像", "", "图像文件 (*.png *.jpg *.jpeg)")

        if not new_image_path:
            return  # 用户取消选择

        # 图像格式兼容性检测
        if not self.is_valid_image_format(new_image_path):
            QMessageBox.warning(self, "无效图像格式", "请选择 PNG 或 JPG 格式的图像文件。")
            return

        # 获取旧图像的完整路径
        old_image_path = os.path.join("recorded_images", old_image_name)

        # 替换文件系统中的图像
        try:
            # 删除旧图像
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

            # 复制新图像到图像目录
            new_image_name = os.path.basename(new_image_path)
            new_image_target_path = os.path.join("recorded_images", new_image_name)
            os.rename(new_image_path, new_image_target_path)
        except Exception as e:
            QMessageBox.critical(self, "图像替换失败", f"无法替换图像：{str(e)}")
            return

        # 更新脚本中的图像引用路径
        for step in self.script:
            try:
                locator = step["locator"]  # 直接访问而不使用 .get()
                if locator["by"] == "image" and os.path.basename(locator["value"]) == old_image_name:
                    step["locator"]["value"] = new_image_target_path  # 替换路径
                    break
            except KeyError as e:
                log(f"[图像引用更新失败] 缺少键: {e}")

        # 更新图像列表并刷新显示
        self.update_image_list(self.script)
        QMessageBox.information(self, "替换成功", f"图像 {old_image_name} 已成功替换为 {new_image_name}")
