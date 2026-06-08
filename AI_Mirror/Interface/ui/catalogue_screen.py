from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QScrollArea, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class ClickableProductCard(QFrame):
    def __init__(self, product, on_clicked):
        super().__init__()

        self.product = product
        self.on_clicked = on_clicked

    def mousePressEvent(self, event):
        self.on_clicked(self.product)


class CatalogueScreen(QWidget):
    def __init__(self, on_product_selected, on_back, on_map):
        super().__init__()

        self.on_product_selected = on_product_selected
        self.on_back = on_back
        self.on_map = on_map

        self.department = None
        self.category = None
        self.products = []

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(40, 30, 40, 30)
        self.main_layout.setSpacing(20)

        # -------------------------
        # TOP BAR
        # -------------------------
        top_bar = QHBoxLayout()

        self.title = QLabel("Catalogue")
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

        top_bar.addWidget(self.title)
        top_bar.addStretch()
        top_bar.addWidget(self.map_button)

        # -------------------------
        # HORIZONTAL SCROLL AREA
        # -------------------------
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #111111;
            }

            QScrollBar:horizontal {
                height: 18px;
                background: #222222;
                border-radius: 9px;
            }

            QScrollBar::handle:horizontal {
                background: #666666;
                border-radius: 9px;
                min-width: 80px;
            }

            QScrollBar::handle:horizontal:hover {
                background: #888888;
            }
        """)

        self.product_container = QWidget()

        # Horizontal layout holds pages/columns
        self.product_layout = QHBoxLayout()
        self.product_layout.setSpacing(30)
        self.product_layout.setContentsMargins(10, 10, 10, 10)

        self.product_container.setLayout(self.product_layout)
        self.scroll_area.setWidget(self.product_container)

        # -------------------------
        # BACK BUTTON
        # -------------------------
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
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)

        self.setLayout(self.main_layout)
        self.setStyleSheet("background-color: #111111;")

    def get_project_root(self):
        return Path(__file__).resolve().parents[1]

    def set_products(self, department, category, products):
        self.department = department
        self.category = category
        self.products = products

        self.title.setText(f"{department} / {category}")
        self.load_product_cards()

    def load_product_cards(self):
        self.clear_products()

        if not self.products:
            empty_label = QLabel("No products available in this section.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("""
                font-size: 24px;
                color: #cccccc;
                padding: 80px;
            """)
            self.product_layout.addWidget(empty_label)
            return

        # ---------------------------------------------------
        # 2 COLUMNS PER SCREEN STYLE
        # Each page contains 2 product cards side-by-side.
        # User scrolls horizontally to see next 2 products.
        # ---------------------------------------------------
        products_per_page = 2

        for page_start in range(0, len(self.products), products_per_page):
            page_products = self.products[page_start:page_start + products_per_page]

            page = QWidget()
            page.setFixedWidth(1050)

            page_layout = QGridLayout()
            page_layout.setSpacing(30)
            page_layout.setContentsMargins(10, 20, 10, 20)

            for index, product in enumerate(page_products):
                card = self.create_product_card(product)

                row = 0
                col = index

                page_layout.addWidget(card, row, col)

            page.setLayout(page_layout)
            self.product_layout.addWidget(page)

        self.product_layout.addStretch()

    def create_product_card(self, product):
        card = ClickableProductCard(product, self.on_product_selected)

        card.setFixedSize(500, 560)
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet("""
            QFrame {
                background-color: #1f1f1f;
                border: 1px solid #333333;
                border-radius: 22px;
            }
            QFrame:hover {
                background-color: #252525;
                border: 2px solid #2d89ef;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(14)

        # -------------------------
        # PRODUCT IMAGE
        # -------------------------
        image_box = QLabel()
        image_box.setFixedSize(450, 300)
        image_box.setAlignment(Qt.AlignCenter)
        image_box.setStyleSheet("""
            QLabel {
                background-color: #333333;
                color: #aaaaaa;
                border-radius: 16px;
                font-size: 18px;
            }
        """)

        image_from_json = product.get("image", "")
        image_path = self.get_project_root() / image_from_json

        if image_path.exists():
            pixmap = QPixmap(str(image_path))

            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    430,
                    280,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                image_box.setPixmap(pixmap)
            else:
                image_box.setText("Image Error")
        else:
            image_box.setText("No Image")

        # -------------------------
        # PRODUCT TEXT
        # -------------------------
        name = QLabel(product.get("name", "Unnamed Product"))
        name.setWordWrap(True)
        name.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
        """)

        price = QLabel(str(product.get("price", "N/A")))
        price.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #00ff99;
        """)

        colour = QLabel(f"Colour: {product.get('colour', 'N/A')}")
        colour.setStyleSheet("""
            font-size: 18px;
            color: #cccccc;
        """)

        sizes = product.get("sizes", [])
        if isinstance(sizes, list):
            size_text = ", ".join(sizes)
        else:
            size_text = str(sizes)

        sizes_label = QLabel(f"Sizes: {size_text}")
        sizes_label.setStyleSheet("""
            font-size: 18px;
            color: #cccccc;
        """)

        location = QLabel(product.get("location", "Location unavailable"))
        location.setWordWrap(True)
        location.setStyleSheet("""
            font-size: 16px;
            color: #aaaaaa;
        """)

        tap_hint = QLabel("Touch product to view details")
        tap_hint.setAlignment(Qt.AlignCenter)
        tap_hint.setStyleSheet("""
            font-size: 16px;
            color: #2d89ef;
            margin-top: 8px;
        """)

        layout.addWidget(image_box, alignment=Qt.AlignCenter)
        layout.addWidget(name)
        layout.addWidget(price)
        layout.addWidget(colour)
        layout.addWidget(sizes_label)
        layout.addWidget(location)

        if product.get("discount"):
            discount = QLabel("DISCOUNT AVAILABLE")
            discount.setStyleSheet("""
                font-size: 17px;
                font-weight: bold;
                color: #ffcc00;
            """)
            layout.addWidget(discount)

        layout.addStretch()
        layout.addWidget(tap_hint)

        card.setLayout(layout)

        return card

    def clear_products(self):
        while self.product_layout.count():
            item = self.product_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()