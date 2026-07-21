from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SystemDiagnosticsScreen(QWidget):
    def __init__(self, health_service, camera_status, on_reset_camera, on_back):
        super().__init__()
        self.health_service = health_service
        self.camera_status = camera_status
        self.on_reset_camera = on_reset_camera
        self.on_back = on_back
        self.value_labels = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(45, 30, 45, 35)
        layout.setSpacing(20)

        title = QLabel("System Diagnostics")
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: white;")
        subtitle = QLabel(
            "Live operational health for this mirror. No customer images or personal data are stored."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("font-size: 18px; color: #b8c0c8;")

        grid = QGridLayout()
        grid.setSpacing(14)
        cards = (
            ("uptime", "Application Uptime"),
            ("camera", "Camera"),
            ("database", "Database"),
            ("memory", "Memory Usage"),
            ("cpu", "CPU Usage"),
            ("disk", "Free Disk Space"),
            ("frames", "Camera Frames"),
            ("reconnects", "Camera Recoveries"),
        )
        for index, (key, label) in enumerate(cards):
            grid.addWidget(self._create_card(key, label), index // 4, index % 4)

        reset_button = QPushButton("Reset Camera Safely")
        reset_button.setFixedSize(230, 54)
        reset_button.setStyleSheet(self._button_style("#2d89ef", "#1b5fbd"))
        reset_button.clicked.connect(self._reset_camera)

        refresh_button = QPushButton("Refresh Now")
        refresh_button.setFixedSize(180, 54)
        refresh_button.setStyleSheet(self._button_style("#00a86b", "#007a4d"))
        refresh_button.clicked.connect(self.refresh)

        back_button = QPushButton("Back")
        back_button.setFixedSize(160, 54)
        back_button.setStyleSheet(self._button_style("#444444", "#666666"))
        back_button.clicked.connect(self.on_back)

        actions = QHBoxLayout()
        actions.addWidget(reset_button)
        actions.addWidget(refresh_button)
        actions.addStretch()
        actions.addWidget(back_button)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(grid)
        layout.addStretch()
        layout.addLayout(actions)
        self.setStyleSheet("background-color: #10151c;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)

    def _create_card(self, key, title):
        card = QFrame()
        card.setMinimumHeight(130)
        card.setStyleSheet(
            "QFrame { background-color: #1c2530; border: 1px solid #34404d; "
            "border-radius: 16px; }"
        )
        layout = QVBoxLayout(card)
        label = QLabel(title)
        label.setStyleSheet("font-size: 16px; color: #aab4bf; border: none;")
        value = QLabel("Checking...")
        value.setAlignment(Qt.AlignCenter)
        value.setWordWrap(True)
        value.setStyleSheet(
            "font-size: 23px; font-weight: bold; color: white; border: none;"
        )
        layout.addWidget(label)
        layout.addWidget(value, stretch=1)
        self.value_labels[key] = value
        return card

    def refresh(self):
        camera = self.camera_status()
        health = self.health_service.snapshot(camera)
        self.value_labels["uptime"].setText(
            self.health_service.format_uptime(health["uptime_seconds"])
        )
        self.value_labels["camera"].setText(camera.get("state", "unknown").title())
        self.value_labels["database"].setText(health["database"])
        memory = health["memory_mb"]
        cpu = health["cpu_percent"]
        self.value_labels["memory"].setText(f"{memory} MB" if memory is not None else "Unavailable")
        self.value_labels["cpu"].setText(f"{cpu}%" if cpu is not None else "Unavailable")
        self.value_labels["disk"].setText(f"{health['disk_free_gb']} GB")
        self.value_labels["frames"].setText(str(camera.get("frames_received", 0)))
        self.value_labels["reconnects"].setText(str(camera.get("reconnect_count", 0)))

    def _reset_camera(self):
        self.on_reset_camera()
        self.refresh()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()
        self.timer.start(2000)

    def hideEvent(self, event):
        self.timer.stop()
        super().hideEvent(event)

    @staticmethod
    def _button_style(colour, hover):
        return f"""
            QPushButton {{
                font-size: 17px; font-weight: bold; color: white;
                background-color: {colour}; border-radius: 11px;
            }}
            QPushButton:hover {{ background-color: {hover}; }}
        """
