from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QTabWidget
from core.recorder import Recorder
from core.script_manager import ScriptManager
from core.config_manager import ConfigManager
from core.test_executor import TestExecutor
from ui.script_editor import ScriptEditor
from ui.report_viewer import ReportViewer
from ui.user_admin import UserAdminPage
from ui.config_page import ConfigPage
from utils.logger import log
from utils.session import clear_login
import threading

class MainWindow(QWidget):
    def __init__(self, username, role):
        super().__init__()
        self.setWindowTitle(f"主界面—{username}（{role}）")
        self.resize(800, 600)


        # 核心组件
        self.recorder = Recorder()
        self.manager  = ScriptManager()
        cfg           = ConfigManager().load_all()
        self.executor = TestExecutor(cfg)

        # UI Tabs
        tabs = QTabWidget()
        # 录制/回放
        self.record_btn = QPushButton("开始录制"); self.stop_btn = QPushButton("停止录制");
        self.play_btn   = QPushButton("回放脚本")
        rec_tab = QWidget()
        rec_layout = QVBoxLayout()
        rec_layout.addWidget(self.record_btn); rec_layout.addWidget(self.stop_btn); rec_layout.addWidget(self.play_btn)
        rec_tab.setLayout(rec_layout)
        tabs.addTab(rec_tab, "录制/回放")
        # 脚本编辑
        tabs.addTab(ScriptEditor(self.manager), "脚本编辑")
        # 报告查看
        tabs.addTab(ReportViewer(), "报告查看")
        # 用户管理（仅管理员可见）
        if role == "admin":
            tabs.addTab(UserAdminPage(), "用户管理")
        # 系统配置
        tabs.addTab(ConfigPage(), "系统配置")

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)
        self.logout_btn = QPushButton("退出登录")  # ⬅️ 新增按钮
        layout.addWidget(self.logout_btn)  # ⬅️ 添加到底部布局
        # 信号绑定
        self.record_btn.clicked.connect(self.start_record)
        self.stop_btn.clicked.connect(self.stop_record)
        self.play_btn.clicked.connect(self.start_play)
        # 按钮绑定
        self.logout_btn.clicked.connect(self.logout)

    def start_record(self):
        log("开始录制")
        self.recorder.start()

    def stop_record(self):
        script = self.recorder.stop()
        self.manager.save(script)
        log(f"脚本保存，共 {len(script)} 步")

    def start_play(self):
        script = self.manager.load_latest()
        def _play():
            try:
                self.executor.run_script(script)
                log("回放完成")
            except Exception:
                log("回放中断")
        threading.Thread(target=_play).start()

    def logout(self):
        clear_login()       # 清除 session
        self.close()        # 关闭主窗口
        self.login = LoginWindow()  # 打开登录窗口
        self.login.show()
