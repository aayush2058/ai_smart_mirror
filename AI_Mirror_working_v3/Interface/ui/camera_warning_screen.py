from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt


class CameraWarningScreen(QWidget):
    def __init__(self, on_cancel, on_agree):
        super().__init__()

        self.on_cancel = on_cancel
        self.on_agree = on_agree
        self.product = None

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(60, 45, 60, 40)
        main_layout.setSpacing(25)

        # -------------------------
        # TITLE
        # -------------------------
        title = QLabel("Camera Usage Notice")
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

        # -------------------------
        # WARNING CARD
        # -------------------------
        warning_card = QFrame()
        warning_card.setStyleSheet("""
            QFrame {
                background-color: #1f1f1f;
                border-radius: 24px;
                border: none;
            }
        """)

        warning_layout = QVBoxLayout()
        warning_layout.setContentsMargins(50, 45, 50, 45)
        warning_layout.setSpacing(24)

        self.product_label = QLabel("")
        self.product_label.setAlignment(Qt.AlignCenter)
        self.product_label.setStyleSheet("""
            QLabel {
                font-size: 26px;
                font-weight: bold;
                color: #00ff99;
                background-color: transparent;
                border: none;
            }
        """)

        message = QLabel(
            "This mirror will activate the camera only for live virtual try-on.\n\n"
            "No photo or video will be saved.\n"
            "The camera will turn off when you exit try-on mode.\n\n"
            "Please stand fully visible in front of the mirror before starting."
        )
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        message.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #dddddd;
                line-height: 140%;
                background-color: transparent;
                border: none;
            }
        """)

        button_row = QHBoxLayout()
        button_row.setSpacing(25)

        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(220, 65)
        cancel_button.setStyleSheet("""
            QPushButton {
                font-size: 22px;
                background-color: #444444;
                color: white;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        cancel_button.clicked.connect(self.on_cancel)

        agree_button = QPushButton("I Agree, Start Try-On")
        agree_button.setFixedSize(320, 65)
        agree_button.setStyleSheet("""
            QPushButton {
                font-size: 22px;
                font-weight: bold;
                background-color: #00a86b;
                color: white;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #007a4d;
            }
        """)
        agree_button.clicked.connect(self.handle_agree)

        button_row.addStretch()
        button_row.addWidget(cancel_button)
        button_row.addWidget(agree_button)
        button_row.addStretch()

        warning_layout.addWidget(self.product_label)
        warning_layout.addWidget(message)
        warning_layout.addSpacing(20)
        warning_layout.addLayout(button_row)

        warning_card.setLayout(warning_layout)


        main_layout.addWidget(title)
        main_layout.addStretch()
        main_layout.addWidget(warning_card)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #111111;")

    def set_product(self, product):
        self.product = product

        if product:
            self.product_label.setText(
                f"Selected item: {product.get('name', 'Unnamed Product')}"
            )
        else:
            self.product_label.setText("No product selected")

    def handle_agree(self):
        if self.product:
            self.on_agree(self.product)