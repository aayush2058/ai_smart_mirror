from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class ProductDetailScreen(QWidget):
    def __init__(self, on_back, on_try_on, on_map):
        super().__init__()

        self.on_back = on_back
        self.on_try_on = on_try_on
        self.on_map = on_map
        self.product = None

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(50, 35, 50, 35)
        self.main_layout.setSpacing(25)

        # -------------------------
        # TOP BAR
        # -------------------------
        top_bar = QHBoxLayout()

        self.title = QLabel("Product Detail")
        self.title.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: white;
        """)

        self.map_button = QPushButton("Map")
        self.map_button.setFixedSize(120, 50)
        self.map_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                background-color: #2d89ef;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #1b5fbd;
            }
        """)
        self.map_button.clicked.connect(self.on_map)

        self.top_try_on_button = QPushButton("Virtual Try On")
        self.top_try_on_button.setFixedSize(190, 50)
        self.top_try_on_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                background-color: #00a86b;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #007a4d;
            }
        """)
        self.top_try_on_button.clicked.connect(self.handle_try_on)

        right_buttons = QVBoxLayout()
        right_buttons.setSpacing(10)
        right_buttons.addWidget(self.map_button)
        right_buttons.addWidget(self.top_try_on_button)

        top_bar.addWidget(self.title)
        top_bar .addStretch()
        top_bar.addLayout(right_buttons)

        # -------------------------
        # CONTENT AREA
        # -------------------------
        content_layout = QHBoxLayout()
        content_layout.setSpacing(40)

        # Product image
        self.image_box = QLabel("No Image")
        self.image_box.setFixedSize(430, 500)
        self.image_box.setAlignment(Qt.AlignCenter)
        self.image_box.setStyleSheet("""
            QLabel {
                background-color: #222222;
                color: #aaaaaa;
                border-radius: 20px;
                font-size: 22px;
            }
        """)

        # Product info card
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background-color: #1f1f1f;
                border-radius: 20px;
                border: 1px solid #333333;
            }
        """)

        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(35, 35, 35, 35)
        info_layout.setSpacing(15)

        self.name_label = QLabel("")
        self.name_label.setStyleSheet("""
            font-size: 34px;
            font-weight: bold;
            color: white;
        """)

        self.price_label = QLabel("")
        self.price_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #00ff99;
        """)

        self.colour_label = QLabel("")
        self.size_label = QLabel("")
        self.available_label = QLabel("")
        self.location_label = QLabel("")
        self.discount_label = QLabel("")

        detail_style = """
            font-size: 21px;
            color: #dddddd;
        """

        self.colour_label.setStyleSheet(detail_style)
        self.size_label.setStyleSheet(detail_style)
        self.available_label.setStyleSheet(detail_style)
        self.location_label.setStyleSheet(detail_style)

        self.discount_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #ffcc00;
        """)

        self.recommendation_title = QLabel("Complete Your Outfit")
        self.recommendation_title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: white;
            margin-top: 20px;
        """)

        self.recommendation_label = QLabel("")
        self.recommendation_label.setWordWrap(True)
        self.recommendation_label.setStyleSheet("""
            font-size: 19px;
            color: #cccccc;
        """)

        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.price_label)
        info_layout.addSpacing(10)
        info_layout.addWidget(self.colour_label)
        info_layout.addWidget(self.size_label)
        info_layout.addWidget(self.available_label)
        info_layout.addWidget(self.location_label)
        info_layout.addWidget(self.discount_label)
        info_layout.addWidget(self.recommendation_title)
        info_layout.addWidget(self.recommendation_label)
        info_layout.addStretch()

        # Buttons
        button_row = QHBoxLayout()
        button_row.setSpacing(15)

        self.try_on_button = QPushButton("Virtual Try On")
        self.try_on_button.setFixedSize(220, 65)
        self.try_on_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                background-color: #00a86b;
                color: white;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: #007a4d;
            }
        """)
        self.try_on_button.clicked.connect(self.handle_try_on)

        self.find_button = QPushButton("Find in Store")
        self.find_button.setFixedSize(220, 65)
        self.find_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                background-color: #2d89ef;
                color: white;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: #1b5fbd;
            }
        """)
        self.find_button.clicked.connect(self.on_map)

        button_row.addWidget(self.try_on_button)
        button_row.addWidget(self.find_button)

        info_layout.addLayout(button_row)

        info_card.setLayout(info_layout)

        content_layout.addWidget(self.image_box)
        content_layout.addWidget(info_card)

        # Back button
        self.back_button = QPushButton("Back")
        self.back_button.setFixedSize(180, 55)
        self.back_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                background-color: #444444;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        self.back_button.clicked.connect(self.on_back)

        self.main_layout.addLayout(top_bar)
        self.main_layout.addLayout(content_layout)
        self.main_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)

        self.setLayout(self.main_layout)
        self.setStyleSheet("background-color: #111111;")

    def set_product(self, product):
        self.product = product
        self.load_product_data()

    def get_project_root(self):
        return Path(__file__).resolve().parents[1]

    def load_product_data(self):
        if not self.product:
            return

        self.title.setText("Product Detail")
        self.name_label.setText(self.product.get("name", "Unnamed Product"))
        self.price_label.setText(str(self.product.get("price", "N/A")))
        self.colour_label.setText(f"Colour: {self.product.get('colour', 'N/A')}")

        sizes = self.product.get("sizes", [])
        if isinstance(sizes, list):
            sizes_text = ", ".join(sizes)
        else:
            sizes_text = str(sizes)

        self.size_label.setText(f"Sizes: {sizes_text}")

        available = self.product.get("available", False)
        if available:
            self.available_label.setText("Availability: In stock")
        else:
            self.available_label.setText("Availability: Out of stock")

        self.location_label.setText(
            f"Location: {self.product.get('location', 'Location unavailable')}"
        )

        if self.product.get("discount"):
            self.discount_label.setText("Discount available on this product")
        else:
            self.discount_label.setText("")

        self.recommendation_label.setText(
            self.get_basic_recommendations(self.product)
        )

        self.load_product_image()

    def load_product_image(self):
        image_from_json = self.product.get("image", "")
        image_path = self.get_project_root() / image_from_json

        print("DETAIL IMAGE PATH:", image_path)
        print("DETAIL IMAGE EXISTS:", image_path.exists())

        if image_path.exists():
            pixmap = QPixmap(str(image_path))

            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    400,
                    470,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_box.setPixmap(pixmap)
            else:
                self.image_box.setText("Image Error")
        else:
            self.image_box.setText("No Image")

    def get_basic_recommendations(self, product):
        tryon_category = product.get("tryon_category", "")
        category = product.get("category", "")

        if tryon_category == "Shirts" or category == "Upper Fit":
            return "Recommended: Blue Denim Jeans, Black Summer Shorts, Trainers, Lightweight Jacket."

        if tryon_category == "Pants" or category == "Lower Fit":
            return "Recommended: Blue Casual T-Shirt, White Slim Fit Top, Hoodie, Casual Shoes."

        return "Recommended matching items will appear here."

    def handle_try_on(self):
        if self.product:
            self.on_try_on(self.product)