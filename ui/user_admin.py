from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout
from core.user_manager import UserManager

class UserAdmin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("用户管理")
        self.um = UserManager()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["用户ID", "用户名", "角色", "邮箱", "创建时间"])

        self.refresh_btn = QPushButton("刷新")
        self.delete_btn = QPushButton("删除所选用户")
        self.role_btn = QPushButton("切换角色")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.role_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.refresh_btn.clicked.connect(self.load_users)
        self.delete_btn.clicked.connect(self.delete_user)
        self.role_btn.clicked.connect(self.change_user_role)

        self.load_users()

    def load_users(self):
        self.table.setRowCount(0)
        users = self.um.list_users()
        for row, user in enumerate(users):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(user["user_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(user["username"]))
            self.table.setItem(row, 2, QTableWidgetItem(user["role"]))
            self.table.setItem(row, 3, QTableWidgetItem(user["email"] or ""))
            self.table.setItem(row, 4, QTableWidgetItem(user["created_at"]))

    def delete_user(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "未选择", "请先选择一个用户")
            return
        uid = int(self.table.item(row, 0).text())
        username = self.table.item(row, 1).text()

        if username == "admin":
            QMessageBox.warning(self, "禁止操作", "不能删除管理员账号")
            return

        confirm = QMessageBox.question(self, "确认删除", f"是否删除用户 {username}？")
        if confirm == QMessageBox.Yes:
            self.um.delete_user(uid)
            self.load_users()
            QMessageBox.information(self, "删除成功", f"用户 {username} 已删除")

    def change_user_role(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "未选择", "请先选择一个用户")
            return
        uid = int(self.table.item(row, 0).text())
        username = self.table.item(row, 1).text()
        role = self.table.item(row, 2).text()
        new_role = "admin" if role == "user" else "user"

        self.um.update_user_role(uid, new_role)
        self.load_users()
        QMessageBox.information(self, "角色修改", f"用户 {username} 的角色已修改为：{new_role}")
