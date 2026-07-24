import cv2

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget
)


class BasketScreen(QWidget):
    def __init__(self, basket_service, on_back, on_clear):
        super().__init__()
        self.basket_service = basket_service
        self.on_back = on_back
        self.on_clear = on_clear

        layout = QVBoxLayout(self)
        layout.setContentsMargins(45, 30, 45, 35)
        title = QLabel("Your Smart Basket")
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: white;")
        subtitle = QLabel("Review your items, then scan the QR code or show it to a store colleague.")
        subtitle.setStyleSheet("font-size: 18px; color: #bbbbbb;")
        subtitle.setWordWrap(True)

        body = QHBoxLayout()
        self.items_label = QLabel()
        self.items_label.setAlignment(Qt.AlignTop)
        self.items_label.setWordWrap(True)
        self.items_label.setStyleSheet(
            "font-size: 20px; color: white; background: #1c2530; "
            "padding: 24px; border-radius: 16px;"
        )
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.items_label)
        scroll.setStyleSheet("border: none; background: #10151c;")

        self.qr_label = QLabel("Basket is empty")
        self.qr_label.setFixedSize(390, 390)
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setStyleSheet(
            "background: white; color: #222; border-radius: 16px; font-size: 18px;"
        )
        body.addWidget(scroll, stretch=1)
        body.addWidget(self.qr_label)

        clear_button = QPushButton("Clear Basket")
        clear_button.setObjectName("clearButton")
        clear_button.setFixedSize(180, 54)
        clear_button.clicked.connect(self.clear_basket)
        back_button = QPushButton("Continue Shopping")
        back_button.setFixedSize(220, 54)
        back_button.clicked.connect(self.on_back)
        for button in (clear_button, back_button):
            button.setStyleSheet(
                "font-size: 17px; font-weight: bold; color: white; "
                "background: #2d89ef; border-radius: 11px;"
            )
        actions = QHBoxLayout()
        actions.addWidget(clear_button)
        actions.addStretch()
        actions.addWidget(back_button)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(body, stretch=1)
        layout.addLayout(actions)
        self.setStyleSheet("background: #10151c;")

    def refresh(self):
        items = self.basket_service.items
        if not items:
            self.items_label.setText("Your basket is empty.")
            self.qr_label.clear()
            self.qr_label.setText("Basket is empty")
            return

        lines = []
        for item in items:
            lines.append(
                f"{item['name']}\nSize: {item['size']}  |  Qty: {item['quantity']}  |  "
                f"£{item['price'] * item['quantity']:.2f}\nLocation: {item['location'] or 'Ask a colleague'}"
            )
        original = self.basket_service.original_total()
        savings = self.basket_service.savings_total()
        if savings > 0:
            lines.append(f"\nOriginal total: £{original:.2f}\nYOU SAVE: £{savings:.2f}")
        lines.append(f"FINAL TOTAL: £{self.basket_service.total():.2f}")
        self.items_label.setText("\n\n".join(lines))

        encoder = cv2.QRCodeEncoder_create()
        qr = encoder.encode(self.basket_service.qr_payload())
        image = QImage(qr.data, qr.shape[1], qr.shape[0], qr.strides[0], QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(image.copy()).scaled(
            350, 350, Qt.KeepAspectRatio, Qt.FastTransformation
        )
        self.qr_label.setPixmap(pixmap)

    def clear_basket(self):
        self.basket_service.clear()
        self.on_clear()
        self.refresh()
