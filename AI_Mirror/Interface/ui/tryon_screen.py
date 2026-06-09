from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt


class TryOnScreen(QWidget):
    def __init__(self, on_exit):
        super().__init__()

        self.on_exit = on_exit
        self.product = None

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(60, 45, 60, 45)
        main_layout.setSpacing(25)

        title = QLabel("Virtual Try-On")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 44px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        self.product_label = QLabel("No product selected")
        self.product_label.setAlignment(Qt.AlignCenter)
        self.product_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #00ff99;
                background-color: transparent;
                border: none;
            }
        """)

        camera_area = QFrame()
        camera_area.setStyleSheet("""
            QFrame {
                background-color: #1f1f1f;
                border-radius: 24px;
                border: none;
            }
        """)

        camera_layout = QVBoxLayout()
        camera_layout.setAlignment(Qt.AlignCenter)
        camera_layout.setSpacing(20)

        camera_text = QLabel(
            "Camera preview will appear here later.\n\n"
            "This placeholder confirms the privacy flow is working."
        )
        camera_text.setAlignment(Qt.AlignCenter)
        camera_text.setStyleSheet("""
            QLabel {
                font-size: 26px;
                color: #dddddd;
                background-color: transparent;
                border: none;
            }
        """)

        camera_layout.addWidget(camera_text)
        camera_area.setLayout(camera_layout)

        exit_button = QPushButton("Exit Try-On")
        exit_button.setFixedSize(240, 65)
        exit_button.setStyleSheet("""
            QPushButton {
                font-size: 22px;
                font-weight: bold;
                background-color: #444444;
                color: white;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        exit_button.clicked.connect(self.on_exit)

        main_layout.addWidget(title)
        main_layout.addWidget(self.product_label)
        main_layout.addWidget(camera_area)
        main_layout.addWidget(exit_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #111111;")

    def set_product(self, product):
        self.product = product

        if product:
            self.product_label.setText(
                f"Trying on: {product.get('name', 'Unnamed Product')}"
            )
        else:
            self.product_label.setText("No product selected")