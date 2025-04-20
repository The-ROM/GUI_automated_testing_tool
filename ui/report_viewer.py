from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QTextEdit, QPushButton, QFileDialog, QMessageBox
from core.db import Database
from PyQt5.QtGui import QTextDocument
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QFileDialog
from utils.logger import log
import time

class ReportViewer(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.setWindowTitle("测试报告查看")
        self.main_window = main_window
        self.db = Database.get_instance()

        self.report_list = QListWidget()
        self.detail_view = QTextEdit()
        self.detail_view.setReadOnly(True)
        self.refresh_btn = QPushButton("刷新列表")
        self.jump_btn = QPushButton("查看关联脚本")
        self.export_btn = QPushButton("导出为 PDF/HTML")
        self.export_btn.clicked.connect(self.export_report)

        layout = QVBoxLayout()
        layout.addWidget(self.report_list)
        layout.addWidget(self.detail_view)
        layout.addWidget(self.refresh_btn)
        layout.addWidget(self.jump_btn)
        layout.addWidget(self.export_btn)
        self.setLayout(layout)

        self.report_list.currentItemChanged.connect(self.show_detail)
        self.refresh_btn.clicked.connect(self.load_reports)
        self.jump_btn.clicked.connect(self.jump_to_editor)
        self.load_reports()

    def load_reports(self):
        """加载所有报告"""
        self.report_list.clear()
        rows = self.db.query("SELECT id, script_id, created_at FROM reports ORDER BY created_at DESC")
        self.reports = rows
        for r in rows:
            self.report_list.addItem(f"报告 #{r['id']} | 脚本 {r['script_id']} | {r['created_at']}")

    def show_detail(self):
        """显示选中报告的详细信息"""
        index = self.report_list.currentRow()
        if index < 0: return
        r = self.reports[index]
        detail = self.db.query("SELECT * FROM reports WHERE id=?", (r["id"],))[0]
        txt = f"""
报告 ID：{detail['id']}
关联脚本：{detail['script_id']}
执行摘要：{detail['summary']}
成功率：{round(detail['success_rate'] * 100, 2)}%
耗时：{detail['duration']} 秒
创建时间：{detail['created_at']}
"""
        self.detail_view.setPlainText(txt.strip())


    def export_report(self):
        """导出报告为PDF或HTML"""
        index = self.report_list.currentRow()
        if index < 0: return
        report = self.reports[index]
        detail = self.db.query("SELECT * FROM reports WHERE id=?", (report["id"],))[0]

        # 生成默认文件名：报告ID + 日期
        current_date = time.strftime("%Y%m%d_%H%M%S")
        default_filename = f"report_{report['id']}_{current_date}"

        # 获取保存路径
        path, _ = QFileDialog.getSaveFileName(self, "导出报告", default_filename,
                                              "PDF 文件 (*.pdf);;HTML 文件 (*.html)")
        if not path:
            return  # 如果用户取消选择，则返回

        # 直接通过字段名访问数据
        content = f"""
        <h1>测试报告 #{detail['id']}</h1>
        <p><b>脚本 ID:</b> {detail['script_id']}</p>
        <p><b>成功率:</b> {round(detail['success_rate'] * 100, 2)}%</p>
        <p><b>耗时:</b> {detail['duration']}s</p>
        <p><b>摘要:</b> {detail['summary']}</p>
        <pre>{detail['detail'] if 'detail' in detail else ''}</pre>
        """

        # 根据文件扩展名决定保存为 HTML 或 PDF
        if path.endswith(".pdf"):
            doc = QTextDocument()
            doc.setHtml(content)
            printer = QPrinter()
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(path)
            doc.print_(printer)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

        # 提示用户报告保存成功
        self.show_save_confirmation(path)

    def show_save_confirmation(self, path):
        """显示报告保存成功的提示"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"报告已成功保存到 {path}")
        msg.setWindowTitle("保存成功")
        msg.exec_()

    def jump_to_editor(self):
        """点击查看脚本按钮后，跳转到脚本编辑器"""
        index = self.report_list.currentRow()
        if index >= 0 and self.main_window:
            sid = self.reports[index]["script_id"]  # 获取选中的脚本ID
            self.main_window.open_script_by_id(sid)  # 调用主窗口的函数，跳转到编辑器


