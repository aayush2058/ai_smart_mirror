from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt


class WelcomeScreen(QWidget):
    def __init__(self, on_start):
        super().__init__()

        self.on_start = on_start

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(60, 50, 60, 40)
        main_layout.setSpacing(30)

        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setSpacing(25)

        title = QLabel("Welcome to Smart Mirror")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 52px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        subtitle = QLabel("Browse products, find locations, and try outfits virtually")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #cccccc;
                background-color: transparent;
                border: none;
            }
        """)

        start_button = QPushButton("Start Shopping")
        start_button.setFixedSize(320, 75)
        start_button.setStyleSheet("""
            QPushButton {
                font-size: 25px;
                font-weight: bold;
                background-color: #2d89ef;
                color: white;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: #1b5fbd;
            }
        """)
        start_button.clicked.connect(self.on_start)

        center_layout.addWidget(title)
        center_layout.addWidget(subtitle)
        center_layout.addSpacing(35)
        center_layout.addWidget(start_button, alignment=Qt.AlignCenter)


        main_layout.addStretch()
        main_layout.addLayout(center_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #111111;")