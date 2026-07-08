from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QFrame
)
from PySide6.QtCore import Qt


class AdminLoginScreen(QWidget):
    def __init__(self, on_login, on_cancel):
        super().__init__()

        self.on_login = on_login
        self.on_cancel = on_cancel

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(60, 45, 60, 45)
        main_layout.setSpacing(25)

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------
        title = QLabel("Staff Login")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 42px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        subtitle = QLabel(
            "Authorised staff members only"
        )
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 20px;
                color: #aaaaaa;
                background-color: transparent;
                border: none;
            }
        """)

        # -------------------------------------------------
        # LOGIN CARD
        # -------------------------------------------------
        login_card = QFrame()
        login_card.setFixedWidth(520)
        login_card.setStyleSheet("""
            QFrame {
                background-color: #1f1f1f;
                border-radius: 22px;
                border: none;
            }
        """)

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(45, 40, 45, 40)
        form_layout.setSpacing(18)

        username_label = QLabel("Username")
        username_label.setStyleSheet("""
            QLabel {
                font-size: 19px;
                color: white;
                border: none;
            }
        """)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(
            "Enter username"
        )
        self.username_input.setFixedHeight(55)
        self.username_input.setStyleSheet("""
            QLineEdit {
                font-size: 19px;
                color: white;
                background-color: #2a2a2a;
                border: 1px solid #555555;
                border-radius: 12px;
                padding-left: 15px;
                padding-right: 15px;
            }

            QLineEdit:focus {
                border: 2px solid #2d89ef;
            }
        """)

        password_label = QLabel("Password")
        password_label.setStyleSheet("""
            QLabel {
                font-size: 19px;
                color: white;
                border: none;
            }
        """)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(
            "Enter password"
        )
        self.password_input.setEchoMode(
            QLineEdit.Password
        )
        self.password_input.setFixedHeight(55)
        self.password_input.setStyleSheet("""
            QLineEdit {
                font-size: 19px;
                color: white;
                background-color: #2a2a2a;
                border: 1px solid #555555;
                border-radius: 12px;
                padding-left: 15px;
                padding-right: 15px;
            }

            QLineEdit:focus {
                border: 2px solid #2d89ef;
            }
        """)

        self.show_password_checkbox = QCheckBox(
            "Show password"
        )
        self.show_password_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 17px;
                color: #cccccc;
                background-color: transparent;
                border: none;
                spacing: 8px;
            }
        """)

        self.show_password_checkbox.toggled.connect(
            self.toggle_password_visibility
        )

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet("""
            QLabel {
                font-size: 17px;
                color: #ff6666;
                background-color: transparent;
                border: none;
            }
        """)

        button_row = QHBoxLayout()
        button_row.setSpacing(18)

        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(180, 58)
        cancel_button.setStyleSheet("""
            QPushButton {
                font-size: 19px;
                background-color: #444444;
                color: white;
                border-radius: 13px;
            }

            QPushButton:hover {
                background-color: #666666;
            }
        """)
        cancel_button.clicked.connect(
            self.handle_cancel
        )

        login_button = QPushButton("Login")
        login_button.setFixedSize(180, 58)
        login_button.setStyleSheet("""
            QPushButton {
                font-size: 19px;
                font-weight: bold;
                background-color: #2d89ef;
                color: white;
                border-radius: 13px;
            }

            QPushButton:hover {
                background-color: #1b5fbd;
            }
        """)
        login_button.clicked.connect(
            self.handle_login
        )

        button_row.addStretch()
        button_row.addWidget(cancel_button)
        button_row.addWidget(login_button)
        button_row.addStretch()

        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(
            self.show_password_checkbox
        )
        form_layout.addWidget(self.error_label)
        form_layout.addSpacing(10)
        form_layout.addLayout(button_row)

        login_card.setLayout(form_layout)

        main_layout.addStretch()
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(20)
        main_layout.addWidget(
            login_card,
            alignment=Qt.AlignCenter
        )
        main_layout.addStretch()

        self.setLayout(main_layout)
        self.setStyleSheet(
            "background-color: #111111;"
        )

        self.password_input.returnPressed.connect(
            self.handle_login
        )

    def toggle_password_visibility(self, checked):
        if checked:
            self.password_input.setEchoMode(
                QLineEdit.Normal
            )
        else:
            self.password_input.setEchoMode(
                QLineEdit.Password
            )

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.show_error(
                "Please enter both username and password."
            )
            return

        self.on_login(username, password)

    def handle_cancel(self):
        self.clear_form()
        self.on_cancel()

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.setStyleSheet("""
            QLabel {
                font-size: 17px;
                color: #ff6666;
                background-color: transparent;
                border: none;
            }
        """)

    def clear_error(self):
        self.error_label.setText("")

    def clear_form(self):
        self.username_input.clear()
        self.password_input.clear()
        self.show_password_checkbox.setChecked(False)
        self.clear_error()

    def show_success(self, message):
        self.error_label.setText(message)
        self.error_label.setStyleSheet("""
            QLabel {
                font-size: 17px;
                font-weight: bold;
                color: #00ff99;
                background-color: transparent;
                border: none;
            }
        """)