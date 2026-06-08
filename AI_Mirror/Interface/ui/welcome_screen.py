from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt


class WelcomeScreen(QWidget):
    def __init__(self, on_start):
        super().__init__()

        self.on_start = on_start

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Welcome to Smart Mirror")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: white;
        """)

        subtitle = QLabel("Browse products, find locations, and try outfits virtually")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 22px;
            color: #cccccc;
        """)

        start_button = QPushButton("Start Shopping")
        start_button.setFixedSize(300, 70)
        start_button.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                background-color: #2d89ef;
                color: white;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #1b5fbd;
            }
        """)

        start_button.clicked.connect(self.on_start)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(40)
        layout.addWidget(start_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #111111;")