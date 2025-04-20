from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QCheckBox,
    QSlider, QPushButton, QHBoxLayout, QMessageBox,QSpinBox
)
from PyQt5.QtCore import Qt
import json
import os

CONFIG_FILE = "config.json"

class ConfigPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("系统设置")
        layout = QVBoxLayout()

        # ✅ 加载当前配置
        self.config = self.load_config()

        # ✅ fallback 选项
        self.fallback_checkbox = QCheckBox("图像识别失败时自动 fallback 到坐标")
        self.fallback_checkbox.setChecked(self.config.get("enable_fallback", True))
        layout.addWidget(self.fallback_checkbox)

        # ✅ 置信度滑块
        confidence_label = QLabel("图像识别置信度（推荐 80~95）")
        layout.addWidget(confidence_label)

        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setMinimum(50)
        self.confidence_slider.setMaximum(100)
        self.confidence_slider.setValue(int(self.config.get("image_confidence", 0.8) * 100))
        layout.addWidget(self.confidence_slider)

        self.confidence_value_label = QLabel(f"{self.confidence_slider.value()}%")
        layout.addWidget(self.confidence_value_label)
        # 识别区域大小（录制图像宽度 = 高度）
        layout.addWidget(QLabel("录制图像截图尺寸（px）"))
        self.image_size_spin = QSpinBox()
        self.image_size_spin.setRange(50, 500)
        self.image_size_spin.setValue(self.config.get("image_region_size", 100))
        layout.addWidget(self.image_size_spin)
        # 滑动时更新显示
        self.confidence_slider.valueChanged.connect(
            lambda val: self.confidence_value_label.setText(f"{val}%")
        )

        # ✅ 保存按钮
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_config)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_config(self):
        try:
            self.config["enable_fallback"] = self.fallback_checkbox.isChecked()
            self.config["image_confidence"] = self.confidence_slider.value() / 100.0
            self.config["image_region_size"] = self.image_size_spin.value()

            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)

            QMessageBox.information(self, "保存成功", "配置已保存，将在下次启动时生效")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"写入配置失败: {e}")
