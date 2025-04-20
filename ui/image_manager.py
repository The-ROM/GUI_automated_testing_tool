from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QLabel,
    QPushButton, QHBoxLayout, QMessageBox, QListWidgetItem
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from core.db import Database
from PyQt5.QtWidgets import QMenu, QAction
import os
from utils.logger import log
import json



class ImageManager(QWidget):
    def __init__(self, image_dir="recorded_images"):
        super().__init__()
        self.setWindowTitle("图像预览管理")
        self.image_dir = image_dir
        self.image_list = QListWidget()
        self.image_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.preview_label = QLabel("图像预览区域")
        self.preview_label.setFixedSize(300, 300)
        self.preview_label.setStyleSheet("border: 1px solid gray; background-color: white;")
        self.preview_label.setScaledContents(True)
        self.db = Database.get_instance()

        self.refresh_btn = QPushButton("刷新")
        self.delete_btn = QPushButton("删除所选图像")
        self.cleanup_btn = QPushButton("一键删除未引用图像")
        self.cleanup_btn.clicked.connect(self.delete_unused_images)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.cleanup_btn)


        layout = QVBoxLayout()
        layout.addWidget(self.image_list)
        layout.addLayout(btn_layout)
        layout.addWidget(self.preview_label)
        self.setLayout(layout)

        self.refresh_btn.clicked.connect(self.load_images)
        self.delete_btn.clicked.connect(self.delete_selected_image)
        self.image_list.currentItemChanged.connect(self.show_preview)
        self.image_list.customContextMenuRequested.connect(self.show_context_menu)

        self.load_images()

    def load_images(self):
        self.image_list.clear()
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)

        images = [f for f in os.listdir(self.image_dir) if f.endswith((".png", ".jpg"))]
        for fname in sorted(images):
            item = QListWidgetItem(fname)
            item.setIcon(QIcon(os.path.join(self.image_dir, fname)))
            self.image_list.addItem(item)

    def show_preview(self, current, _):
        if not current:
            self.preview_label.clear()
            return
        fname = current.text()
        path = os.path.join(self.image_dir, fname)
        print(path)
        if os.path.exists(path):
            pixmap = QPixmap(path)
            self.preview_label.setPixmap(pixmap)

            # ✅ 查询脚本使用情况
            # used_in = self.find_scripts_using_image(path)
            # if used_in:
            #     msg = f"被以下脚本引用：{', '.join(map(str, used_in))}"
            #     print(msg)
            # else:
            #     msg = "未在任何脚本中使用"
            #     print(msg)
            # self.setWindowTitle(f"图像预览管理 - {msg}")

    def delete_selected_image(self):
        current = self.image_list.currentItem()
        if not current:
            QMessageBox.warning(self, "未选择", "请先选择要删除的图像")
            return
        fname = current.text()
        path = os.path.join(self.image_dir, fname)
        reply = QMessageBox.question(self, "确认删除", f"确定要删除图像：{fname} 吗？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove(path)
                self.load_images()
                QMessageBox.information(self, "删除成功", f"{fname} 已删除")
            except Exception as e:
                QMessageBox.critical(self, "删除失败", str(e))

    def find_scripts_using_image(self, fname):
        """查找引用当前图像文件名的脚本ID"""
        fname = os.path.basename(fname)
        print(f"fname:{fname}")

        result = []
        rows = self.db.query("SELECT id, content FROM scripts")
        for row in rows:
            try:
                content = row["content"]
                if not content:
                    continue

                script = json.loads(content)
                if not isinstance(script, list):
                    continue

                for step in script:
                    locator = step.get("locator", {})
                    if locator.get("by") == "image":
                        script_image = os.path.basename(locator.get("value", ""))
                        if script_image == fname:
                            result.append(row["id"])
                            break
            except Exception as e:
                QMessageBox.critical(self, "查询脚本失败", str(e))
                log(e)
                continue

        return result

    def show_context_menu(self, position):
        item = self.image_list.itemAt(position)
        if not item:
            return
        fname = os.path.basename(item.text())

        used_ids = self.find_scripts_using_image(fname)
        if used_ids:
            msg = f"图像 [{fname}] 被以下脚本引用：\n" + ", ".join(map(str, used_ids))
        else:
            msg = f"图像 [{fname}] 未在任何脚本中使用"

        QMessageBox.information(self, "引用信息", msg)

    def delete_unused_images(self):
        all_images = set(f for f in os.listdir(self.image_dir) if f.endswith((".png", ".jpg")))
        used_images = set()

        # 遍历数据库中所有脚本，提取引用图像名
        rows = self.db.query("SELECT content FROM scripts")
        for row in rows:
            try:
                script = json.loads(row["content"])
                for step in script:
                    locator = step.get("locator", {})
                    if locator.get("by") == "image":
                        fname = os.path.basename(locator.get("value", ""))
                        used_images.add(fname)
            except Exception:
                continue

        unused = all_images - used_images
        if not unused:
            QMessageBox.information(self, "无可删除项", "没有未使用的图像文件。")
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"共检测到 {len(unused)} 个未被引用的图像。\n是否要删除它们？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        count = 0
        for fname in unused:
            try:
                os.remove(os.path.join(self.image_dir, fname))
                count += 1
            except Exception as e:
                print(f"[删除失败] {fname}: {e}")

        self.load_images()
        QMessageBox.information(self, "清理完成", f"已删除未使用图像 {count} 个。")


