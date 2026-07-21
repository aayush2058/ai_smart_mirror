from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
<<<<<<< HEAD
    QPushButton, QFrame
=======
    QPushButton, QFrame, QComboBox
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from ui.common_widgets import create_map_button


class ProductDetailScreen(QWidget):
<<<<<<< HEAD
    def __init__(self, on_back, on_try_on, on_map):
=======
    def __init__(self, on_back, on_try_on, on_map, on_add_to_basket, on_view_basket):
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
        super().__init__()

        self.on_back = on_back
        self.on_try_on = on_try_on
        self.on_map = on_map
<<<<<<< HEAD
=======
        self.on_add_to_basket = on_add_to_basket
        self.on_view_basket = on_view_basket
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
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
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        self.top_try_button = QPushButton("Virtual Try")
        self.top_try_button.setFixedSize(250, 55)
        self.top_try_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                background-color: #00a86b;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #007a4d;
            }
        """)
        self.top_try_button.clicked.connect(self.handle_try_on)

<<<<<<< HEAD
        top_bar.addWidget(self.title)
        top_bar.addStretch()
=======
        basket_button = QPushButton("View Basket")
        basket_button.setFixedSize(190, 55)
        basket_button.setStyleSheet(self.top_try_button.styleSheet())
        basket_button.clicked.connect(self.on_view_basket)

        top_bar.addWidget(self.title)
        top_bar.addStretch()
        top_bar.addWidget(basket_button)
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
        top_bar.addWidget(self.top_try_button)

        # -------------------------
        # CONTENT AREA
        # -------------------------
        content_layout = QHBoxLayout()
        content_layout.setSpacing(40)

        self.image_box = QLabel("No Image")
        self.image_box.setFixedSize(430, 500)
        self.image_box.setAlignment(Qt.AlignCenter)
        self.image_box.setStyleSheet("""
            QLabel {
                background-color: #222222;
                color: #aaaaaa;
                border-radius: 20px;
                font-size: 22px;
                border: none;
            }
        """)

        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background-color: #1f1f1f;
                border-radius: 20px;
                border: none;
            }
        """)

        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(35, 35, 35, 35)
        info_layout.setSpacing(15)

        self.name_label = QLabel("")
        self.price_label = QLabel("")
        self.colour_label = QLabel("")
        self.size_label = QLabel("")
        self.available_label = QLabel("")
        self.location_label = QLabel("")
        self.discount_label = QLabel("")
        self.recommendation_title = QLabel("Complete Your Outfit")
        self.recommendation_label = QLabel("")
<<<<<<< HEAD
=======
        self.size_selector = QComboBox()
        self.size_selector.setFixedHeight(48)
        self.size_selector.setStyleSheet(
            "font-size: 18px; color: white; background: #293746; "
            "border: 1px solid #496176; border-radius: 10px; padding: 8px;"
        )
        self.add_basket_button = QPushButton("Add Selected Size to Basket")
        self.add_basket_button.setFixedHeight(52)
        self.add_basket_button.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: white; "
            "background: #2d89ef; border-radius: 11px;"
        )
        self.add_basket_button.clicked.connect(self.handle_add_to_basket)
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)

        self.name_label.setWordWrap(True)
        self.location_label.setWordWrap(True)
        self.recommendation_label.setWordWrap(True)

        self.name_label.setStyleSheet("""
            QLabel {
                font-size: 34px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        self.price_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #00ff99;
                background-color: transparent;
                border: none;
            }
        """)

        detail_style = """
            QLabel {
                font-size: 21px;
                color: #dddddd;
                background-color: transparent;
                border: none;
            }
        """

        self.colour_label.setStyleSheet(detail_style)
        self.size_label.setStyleSheet(detail_style)
        self.available_label.setStyleSheet(detail_style)
        self.location_label.setStyleSheet(detail_style)

        self.discount_label.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #ffcc00;
                background-color: transparent;
                border: none;
            }
        """)

        self.recommendation_title.setStyleSheet("""
            QLabel {
                font-size: 26px;
                font-weight: bold;
                color: white;
                margin-top: 20px;
                background-color: transparent;
                border: none;
            }
        """)

        self.recommendation_label.setStyleSheet("""
            QLabel {
                font-size: 19px;
                color: #cccccc;
                background-color: transparent;
                border: none;
            }
        """)

        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.price_label)
        info_layout.addSpacing(10)
        info_layout.addWidget(self.colour_label)
        info_layout.addWidget(self.size_label)
        info_layout.addWidget(self.available_label)
        info_layout.addWidget(self.location_label)
        info_layout.addWidget(self.discount_label)
<<<<<<< HEAD
=======
        info_layout.addWidget(self.size_selector)
        info_layout.addWidget(self.add_basket_button)
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
        info_layout.addWidget(self.recommendation_title)
        info_layout.addWidget(self.recommendation_label)
        info_layout.addStretch()

        info_card.setLayout(info_layout)

        content_layout.addWidget(self.image_box)
        content_layout.addWidget(info_card)

        # -------------------------
        # BOTTOM BAR
        # -------------------------
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(20)

        self.map_button = create_map_button()
        self.map_button.clicked.connect(self.on_map)

        self.back_button = QPushButton("Back")
        self.back_button.setFixedSize(180, 60)
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

        bottom_bar.addWidget(self.map_button, alignment=Qt.AlignLeft)
        bottom_bar.addStretch()
        bottom_bar.addWidget(self.back_button, alignment=Qt.AlignRight)

        self.main_layout.addLayout(top_bar)
        self.main_layout.addLayout(content_layout)
        self.main_layout.addLayout(bottom_bar)

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

        self.name_label.setText(self.product.get("name", "Unnamed Product"))
        self.price_label.setText(str(self.product.get("price", "N/A")))
        self.colour_label.setText(f"Colour: {self.product.get('colour', 'N/A')}")

        sizes = self.product.get("sizes", [])
        if isinstance(sizes, list):
            sizes_text = ", ".join(sizes)
        else:
            sizes_text = str(sizes)

        self.size_label.setText(f"Sizes: {sizes_text}")
<<<<<<< HEAD
=======
        self.size_selector.clear()
        self.size_selector.addItems(sizes if isinstance(sizes, list) else [])
        can_add = bool(sizes) and bool(self.product.get("available"))
        self.size_selector.setEnabled(can_add)
        self.add_basket_button.setEnabled(can_add)
        self.add_basket_button.setText(
            "Add Selected Size to Basket" if can_add else "Currently Unavailable"
        )
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)

        if self.product.get("available", False):
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

<<<<<<< HEAD
=======
        self.top_try_button.setVisible(
            bool(self.product.get("tryon_enabled", False))
        )

>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
        self.load_product_image()

    def load_product_image(self):
        if not self.product:
            return

        image_from_json = self.product.get("image", "")
        image_path = self.get_project_root() / image_from_json

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
            return (
                "Recommended: Blue Denim Jeans, Black Summer Shorts, "
                "Trainers, Lightweight Jacket."
            )

        if tryon_category == "Pants" or category == "Lower Fit":
            return (
                "Recommended: Blue Casual T-Shirt, White Slim Fit Top, "
                "Hoodie, Casual Shoes."
            )

        return "Recommended matching items will appear here."

    def handle_try_on(self):
<<<<<<< HEAD
        if self.product:
            self.on_try_on(self.product)
=======
        if self.product and self.product.get("tryon_enabled", False):
            self.on_try_on(self.product)

    def handle_add_to_basket(self):
        if self.product and self.size_selector.currentText():
            self.on_add_to_basket(self.product, self.size_selector.currentText())
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
