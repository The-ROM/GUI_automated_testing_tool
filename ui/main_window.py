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
from ui.script_history import ScriptHistory
from ui.image_manager import ImageManager
import threading

class MainWindow(QWidget):
    def __init__(self, username, role):
        super().__init__()
        self.setWindowTitle(f"主界面—{username}（{role}）")
        self.resize(800, 600)


        # 核心组件
        cfg           = ConfigManager().load_all()
        self.recorder = Recorder(cfg)
        self.manager  = ScriptManager()
        self.executor = TestExecutor(cfg)

        # UI Tabs
        tabs = QTabWidget()
        # 录制/回放
        self.record_btn = QPushButton("开始录制")
        self.is_recording = False
        self.play_btn   = QPushButton("回放脚本")
        rec_tab = QWidget()
        rec_layout = QVBoxLayout()
        rec_layout.addWidget(self.record_btn);
        rec_layout.addWidget(self.play_btn)
        rec_tab.setLayout(rec_layout)
        tabs.addTab(rec_tab, "录制/回放")
        # 脚本编辑
        self.script_editor = ScriptEditor(self.manager)
        tabs.addTab(self.script_editor, "脚本编辑")
        # 历史脚本
        self.script_history = ScriptHistory(main_window=self)  # 传 self
        tabs.addTab(self.script_history, "历史脚本")
        # 报告查看
        self.report_viewer = ReportViewer(main_window=self)  # 传 self
        tabs.addTab(self.report_viewer, "报告查看")

        # 图像管理
        self.image_manager = ImageManager()
        tabs.addTab(self.image_manager, "图像管理")
        # 用户管理（仅管理员可见）
        if role == "admin":
            tabs.addTab(UserAdminPage(), "用户管理")


        # 系统配置
        tabs.addTab(ConfigPage(), "系统配置")
        self.tabs = tabs

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)
        self.logout_btn = QPushButton("退出登录")  # ⬅️ 新增按钮
        layout.addWidget(self.logout_btn)  # ⬅️ 添加到底部布局
        # 信号绑定
        self.record_btn.clicked.connect(self.toggle_record)
        self.play_btn.clicked.connect(self.start_play)
        # 按钮绑定
        self.logout_btn.clicked.connect(self.logout)

    def open_script_by_id(self, script_id):
        """在脚本编辑器中打开某个脚本"""
        self.script_editor.load_by_id(script_id)
        self.script_editor.setFocus()

    def toggle_record(self):
        if not self.is_recording:
            log("开始录制")
            self.recorder.start()
            self.record_btn.setText("停止录制")
        else:
            script = self.recorder.stop()
            self.manager.save(script)
            log(f"脚本保存，共 {len(script)} 步")
            self.record_btn.setText("开始录制")
        self.is_recording = not self.is_recording

    def start_play(self):
        # 获取最新脚本及其 id
        result = self.manager.load_latest()
        script_id = result['script_id']
        script = result['content']

        if script_id is None:
            log("没有找到可用的脚本")
            return

        def _play():
            try:
                self.executor.run_script(script,script_id)
                log("回放完成")
            except Exception as e:
                log(f"回放中断，错误信息：{e}")  # 记录异常详细信息
                log(f"回放失败的详细堆栈：{str(e)}")
                import traceback
                log(f"回放失败的堆栈信息：\n{traceback.format_exc()}")  # 捕获并打印堆栈信息

        threading.Thread(target=_play).start()

    def logout(self):
        from ui.login_window import LoginWindow
        clear_login()       # 清除 session
        self.close()        # 关闭主窗口
        self.login = LoginWindow()  # 打开登录窗口
        self.login.show()
