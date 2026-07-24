from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QDialog, QFormLayout, QFrame, QHBoxLayout,
                               QLabel, QLineEdit, QMessageBox, QPushButton, QScrollArea,
                               QVBoxLayout, QWidget)


class AccountDialog(QDialog):
    def __init__(self, title, include_username=True, include_role=True):
        super().__init__(); self.setWindowTitle(title); self.setMinimumWidth(480)
        layout = QVBoxLayout(self); form = QFormLayout()
        self.username = QLineEdit(); self.password = QLineEdit(); self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("10+ characters, upper/lower-case and number")
        self.role = QComboBox(); self.role.addItem("Administrator", "admin"); self.role.addItem("Super Administrator", "super_admin")
        style = "font-size:17px;color:white;background:#202b36;border:1px solid #465766;border-radius:9px;padding:9px;"
        for widget in (self.username, self.password, self.role): widget.setMinimumHeight(46); widget.setStyleSheet(style)
        if include_username: form.addRow("Username", self.username)
        form.addRow("Password", self.password)
        if include_role: form.addRow("Role", self.role)
        buttons = QHBoxLayout(); cancel = QPushButton("Cancel"); save = QPushButton("Save")
        cancel.clicked.connect(self.reject); save.clicked.connect(self.accept)
        for button in (cancel, save): button.setFixedSize(140, 46); button.setStyleSheet("font-size:17px;color:white;background:#2d89ef;border-radius:9px;")
        buttons.addStretch(); buttons.addWidget(cancel); buttons.addWidget(save)
        layout.addLayout(form); layout.addLayout(buttons); self.setStyleSheet("background:#121a22;color:white;")


class AccountManagementScreen(QWidget):
    def __init__(self, auth_service, current_user, on_back):
        super().__init__(); self.auth_service = auth_service; self.current_user = current_user
        root = QVBoxLayout(self); root.setContentsMargins(34, 26, 34, 28)
        header = QHBoxLayout(); title = QLabel("Staff Account Management")
        title.setWordWrap(True)
        title.setStyleSheet("font-size:34px;font-weight:bold;color:white;")
        create = QPushButton("Create Account"); create.clicked.connect(self.create_account)
        undo = QPushButton("Undo Account Change"); undo.clicked.connect(self.undo_change)
        back = QPushButton("Back"); back.clicked.connect(on_back)
        for button in (create, undo, back):
            button.setMinimumSize(160, 48); button.setStyleSheet("font-size:16px;color:white;background:#2d6f9f;border-radius:10px;")
        header.addWidget(title, 1); header.addWidget(back)
        actions = QHBoxLayout(); actions.setSpacing(10)
        actions.addWidget(create); actions.addWidget(undo); actions.addStretch()
        note = QLabel("Account creation, enable/disable and password resets are audited. Each action can be undone for 24 hours.")
        note.setWordWrap(True); note.setStyleSheet("font-size:17px;color:#b9c3cc;")
        filters = QHBoxLayout(); filters.setSpacing(9)
        self.search = QLineEdit(); self.search.setPlaceholderText("Search username..."); self.search.setMinimumWidth(230)
        self.role_filter = QComboBox(); self.role_filter.addItem("All roles", None); self.role_filter.addItem("Administrator", "admin"); self.role_filter.addItem("Super Administrator", "super_admin")
        self.status_filter = QComboBox(); self.status_filter.addItems(["All status", "Active", "Disabled"])
        clear = QPushButton("Clear"); clear.setObjectName("clearButton"); clear.clicked.connect(self.clear_filters); self.result_count = QLabel()
        for widget in (self.search, self.role_filter, self.status_filter):
            widget.setMinimumHeight(44); widget.setStyleSheet("font-size:15px;color:white;background:#263441;border:1px solid #4b6072;border-radius:9px;padding:7px;")
        filters.addWidget(self.search, 1); filters.addWidget(self.role_filter); filters.addWidget(self.status_filter); filters.addWidget(clear); filters.addWidget(self.result_count)
        self.search.textChanged.connect(self.apply_filters); self.role_filter.currentIndexChanged.connect(self.apply_filters); self.status_filter.currentIndexChanged.connect(self.apply_filters)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("border:none;background:#10151c;")
        container = QWidget(); self.list_layout = QVBoxLayout(container); self.list_layout.setSpacing(12); scroll.setWidget(container)
        root.addLayout(header); root.addLayout(actions); root.addWidget(note); root.addLayout(filters); root.addWidget(scroll); self.setStyleSheet("background:#10151c;")

    def refresh(self):
        self.users = self.auth_service.list_users(); self.apply_filters()

    def apply_filters(self):
        query = self.search.text().strip().lower(); role = self.role_filter.currentData(); status = self.status_filter.currentText()
        users = [user for user in getattr(self, "users", []) if (not query or query in user["username"].lower())
                 and (not role or user["role"] == role)
                 and (status == "All status" or bool(user["active"]) == (status == "Active"))]
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.result_count.setText(f"{len(users)} accounts")
        for user in users:
            card = QFrame(); card.setStyleSheet("QFrame{background:#1c2530;border:1px solid #34495e;border-radius:13px;}")
            row = QHBoxLayout(card); info = QLabel(
                f'<b>{user["username"]}</b>  ·  {user["role"].replace("_", " ").title()}<br>'
                f'Status: {"Active" if user["active"] else "Disabled"}  ·  Created: {user["created_at"]}  ·  '
                f'Last login: {user["last_login_at"] or "Never"}'
            )
            info.setTextFormat(Qt.RichText); info.setStyleSheet("font-size:16px;color:white;border:none;"); info.setWordWrap(True)
            toggle = QPushButton("Disable" if user["active"] else "Enable")
            toggle.clicked.connect(lambda checked=False, item=user: self.toggle_user(item))
            reset = QPushButton("Reset Password"); reset.clicked.connect(lambda checked=False, item=user: self.reset_password(item))
            for button in (toggle, reset): button.setFixedSize(145, 44); button.setStyleSheet("font-size:15px;color:white;background:#3d6e93;border-radius:9px;")
            if user["id"] == self.current_user()["id"]: toggle.setEnabled(False); toggle.setToolTip("You cannot disable your signed-in account.")
            row.addWidget(info, 1); row.addWidget(reset); row.addWidget(toggle); self.list_layout.addWidget(card)
        self.list_layout.addStretch()

    def clear_filters(self):
        self.search.clear(); self.role_filter.setCurrentIndex(0); self.status_filter.setCurrentIndex(0)

    def create_account(self):
        dialog = AccountDialog("Create Staff Account")
        if dialog.exec() != QDialog.Accepted: return
        try:
            self.auth_service.create_user(dialog.username.text(), dialog.password.text(),
                                          dialog.role.currentData(), self.current_user()["id"])
            QMessageBox.information(self, "Account Created", "The staff account was created successfully.")
            self.refresh()
        except Exception as error:
            QMessageBox.warning(self, "Cannot Create Account", str(error))

    def toggle_user(self, user):
        try:
            self.auth_service.set_user_active(user["id"], not bool(user["active"]), self.current_user()["id"])
            self.refresh()
        except Exception as error: QMessageBox.warning(self, "Account Error", str(error))

    def reset_password(self, user):
        dialog = AccountDialog(f'Reset Password — {user["username"]}', include_username=False, include_role=False)
        if dialog.exec() != QDialog.Accepted: return
        try:
            self.auth_service.reset_password(user["id"], dialog.password.text(), self.current_user()["id"])
            QMessageBox.information(self, "Password Reset", "Password updated. This action is undoable for 24 hours.")
        except Exception as error: QMessageBox.warning(self, "Password Error", str(error))

    def undo_change(self):
        history = [item for item in self.auth_service.account_history() if item["can_undo"]]
        if not history:
            QMessageBox.information(self, "Nothing to Undo", "No account change is currently undoable."); return
        latest = history[0]
        answer = QMessageBox.question(self, "Undo Account Change",
                                      f'Undo: {latest["description"]}\nSaved: {latest["created_display"]}?',
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer != QMessageBox.Yes: return
        success, message = self.auth_service.undo_account_change(latest["id"], self.current_user()["id"])
        QMessageBox.information(self, "Account Undo" if success else "Cannot Undo", message); self.refresh()
