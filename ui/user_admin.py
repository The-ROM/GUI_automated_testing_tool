from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHBoxLayout, QLineEdit, QComboBox, QLabel
)
from core.user_manager import UserManager

class UserAdminPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("用户管理")
        self.um = UserManager()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["用户ID", "用户名", "角色", "邮箱", "创建时间", "状态"])

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索用户名或邮箱")

        self.role_filter = QComboBox()
        self.role_filter.addItems(["全部", "管理员", "普通用户"])

        self.refresh_btn = QPushButton("刷新")
        self.delete_btn = QPushButton("删除所选用户")
        self.role_btn = QPushButton("切换角色")
        self.toggle_btn = QPushButton("启用/禁用")
        self.reset_btn = QPushButton("重置密码")

        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(QLabel("搜索："))
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(QLabel("角色筛选："))
        toolbar_layout.addWidget(self.role_filter)
        toolbar_layout.addWidget(self.refresh_btn)
        toolbar_layout.addWidget(self.delete_btn)
        toolbar_layout.addWidget(self.role_btn)
        toolbar_layout.addWidget(self.toggle_btn)
        toolbar_layout.addWidget(self.reset_btn)

        layout = QVBoxLayout()
        layout.addLayout(toolbar_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.refresh_btn.clicked.connect(self.load_users)
        self.delete_btn.clicked.connect(self.delete_user)
        self.role_btn.clicked.connect(self.change_user_role)
        self.toggle_btn.clicked.connect(self.toggle_user_status)
        self.reset_btn.clicked.connect(self.reset_user_password)
        self.search_input.textChanged.connect(self.load_users)
        self.role_filter.currentIndexChanged.connect(self.load_users)

        self.load_users()

    def load_users(self):
        keyword = self.search_input.text().strip().lower()
        role_filter = self.role_filter.currentText()

        all_users = self.um.list_users()
        users = []

        for user in all_users:
            username = user["username"].lower()
            email = (user["email"] or "").lower()
            if keyword and keyword not in username and keyword not in email:
                continue
            if role_filter == "管理员" and user["role"] != "admin":
                continue
            if role_filter == "普通用户" and user["role"] != "user":
                continue
            users.append(user)

        self.table.setRowCount(0)
        for row, user in enumerate(users):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(user["user_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(user["username"]))
            self.table.setItem(row, 2, QTableWidgetItem(user["role"]))
            self.table.setItem(row, 3, QTableWidgetItem(user["email"] or ""))
            self.table.setItem(row, 4, QTableWidgetItem(user["created_at"]))
            self.table.setItem(row, 5, QTableWidgetItem(user["status"]))

    def get_selected_user(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "未选择", "请先选择一个用户")
            return None
        return {
            "user_id": int(self.table.item(row, 0).text()),
            "username": self.table.item(row, 1).text(),
            "role": self.table.item(row, 2).text()
        }

    def delete_user(self):
        user = self.get_selected_user()
        if not user:
            return
        if user["username"] == "admin":
            QMessageBox.warning(self, "操作无效", "不能删除管理员账号")
            return
        confirm = QMessageBox.question(self, "确认删除", f"确认要删除用户 {user['username']} 吗？")
        if confirm == QMessageBox.Yes:
            self.um.delete_user(user["user_id"])
            self.load_users()
            QMessageBox.information(self, "删除成功", f"已删除用户 {user['username']}")

    def change_user_role(self):
        user = self.get_selected_user()
        if not user:
            return
        new_role = "admin" if user["role"] == "user" else "user"
        self.um.update_user_role(user["user_id"], new_role)
        self.load_users()
        QMessageBox.information(self, "角色已更改", f"用户 {user['username']} 的角色改为 {new_role}")

    def toggle_user_status(self):
        user = self.get_selected_user()
        if not user:
            return
        self.um.toggle_user_status(user["user_id"])
        self.load_users()
        QMessageBox.information(self, "状态更新", f"用户 {user['username']} 状态已变更")

    def reset_user_password(self):
        user = self.get_selected_user()
        if not user:
            return
        self.um.update_password(user["user_id"], "123456")
        QMessageBox.information(self, "密码已重置", f"用户 {user['username']} 的密码已重置为 123456")
