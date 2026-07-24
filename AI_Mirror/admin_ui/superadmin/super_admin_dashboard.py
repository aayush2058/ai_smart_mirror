from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget


class SuperAdminDashboard(QWidget):
    def __init__(self, on_admin, on_predictions, on_accounts, on_insights,
                 on_diagnostics, on_history, on_logout):
        super().__init__()
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("border:none;background:#0d131a;")
        content = QWidget(); layout = QVBoxLayout(content); layout.setContentsMargins(36, 28, 36, 30); layout.setSpacing(18)
        header = QHBoxLayout()
        title = QLabel("Super Admin Control Centre")
        title.setStyleSheet("font-size:36px;font-weight:bold;color:white;")
        badge = QLabel("SUPER ADMIN"); badge.setAlignment(Qt.AlignCenter); badge.setFixedSize(150, 40)
        badge.setStyleSheet("font-size:14px;font-weight:bold;color:#10151c;background:#e9b949;border-radius:10px;")
        logout = QPushButton("Log Out"); logout.setFixedSize(140, 48); logout.clicked.connect(on_logout)
        logout.setStyleSheet("font-size:17px;color:white;background:#8b2d2d;border-radius:10px;")
        header.addWidget(title); header.addWidget(badge); header.addStretch(); header.addWidget(logout)
        subtitle = QLabel("System-wide administration, offline predictions, staff access, operational health and audit controls.")
        subtitle.setWordWrap(True); subtitle.setStyleSheet("font-size:18px;color:#b7c1cb;")
        self.summary = QLabel("Loading system summary…"); self.summary.setWordWrap(True)
        self.summary.setStyleSheet("font-size:18px;color:white;background:#17212b;padding:18px;border:1px solid #304252;border-radius:14px;")
        grid = QGridLayout(); grid.setSpacing(14)
        actions = (
            ("All Admin Controls", "Products, inventory, discounts, locations and try-on", on_admin, "#2d89ef"),
            ("Prediction Dashboard", "Demand forecasts, conversion and stock risk", on_predictions, "#7b5cd6"),
            ("Staff Accounts", "Create, disable, reset and audit accounts", on_accounts, "#008f68"),
            ("Retail Insights", "Anonymous engagement and CSV reports", on_insights, "#397a9f"),
            ("System Diagnostics", "Camera, database, disk and uptime", on_diagnostics, "#4c6b58"),
            ("Product Change History", "Independent 24-hour product Undo", on_history, "#a56527"),
        )
        for index, (name, description, callback, colour) in enumerate(actions):
            button = QPushButton(f"{name}\n{description}"); button.setMinimumHeight(110)
            button.setCursor(Qt.PointingHandCursor); button.clicked.connect(callback)
            button.setStyleSheet(
                f"font-size:17px;font-weight:bold;text-align:left;padding:16px;color:white;"
                f"background:{colour};border:1px solid rgba(255,255,255,45);border-radius:16px;"
            )
            grid.addWidget(button, index // 2, index % 2)
        layout.addLayout(header); layout.addWidget(subtitle); layout.addWidget(self.summary); layout.addLayout(grid); layout.addStretch()
        scroll.setWidget(content); root.addWidget(scroll); self.setStyleSheet("background:#0d131a;")

    def set_summary(self, users, active_users, products, prediction_time):
        prediction = prediction_time or "Not generated yet"
        self.summary.setText(
            f"<b>{active_users}</b> active staff accounts out of {users}  ·  "
            f"<b>{products}</b> active products  ·  Latest prediction: <b>{prediction}</b>"
        )
