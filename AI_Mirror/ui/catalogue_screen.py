from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QLineEdit, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from ui.common_widgets import create_map_button


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
        # PAGE TITLE
        # -------------------------
        self.title = QLabel("Catalogue")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        filters = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products or colours")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Recommended", "Price: Low to High", "Price: High to Low", "Name A-Z"])
        self.stock_only = QCheckBox("In stock only")
        for widget in (self.search_input, self.sort_combo):
            widget.setFixedHeight(48)
            widget.setStyleSheet("font-size:17px;color:white;background:#232a32;border:1px solid #465666;border-radius:10px;padding:8px;")
        self.stock_only.setStyleSheet("font-size:17px;color:white;")
        self.search_input.textChanged.connect(self.load_product_cards)
        self.sort_combo.currentIndexChanged.connect(self.load_product_cards)
        self.stock_only.toggled.connect(self.load_product_cards)
        filters.addWidget(self.search_input, 2); filters.addWidget(self.sort_combo, 1); filters.addWidget(self.stock_only)

        # -------------------------
        # VERTICAL SCROLL AREA
        # -------------------------
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #111111;
            }

            QScrollBar:vertical {
                width: 18px;
                background: #222222;
                border-radius: 9px;
            }

            QScrollBar::handle:vertical {
                background: #666666;
                border-radius: 9px;
                min-height: 80px;
            }

            QScrollBar::handle:vertical:hover {
                background: #888888;
            }
        """)

        self.product_container = QWidget()

        # 2 columns, vertical scrolling
        self.product_grid = QGridLayout()
        self.product_grid.setSpacing(28)
        self.product_grid.setContentsMargins(20, 20, 20, 20)

        self.product_container.setLayout(self.product_grid)
        self.scroll_area.setWidget(self.product_container)

        # -------------------------
        # BOTTOM BAR
        # -------------------------
        bottom_bar = QHBoxLayout()

        self.map_button = create_map_button()
        self.map_button.clicked.connect(self.on_map)

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

        bottom_bar.addWidget(self.map_button, alignment=Qt.AlignLeft)
        bottom_bar.addStretch()
        bottom_bar.addWidget(self.back_button, alignment=Qt.AlignRight)

        self.main_layout.addWidget(self.title)
        self.main_layout.addLayout(filters)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addLayout(bottom_bar)

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

        query = self.search_input.text().strip().lower()
        products = [product for product in self.products
                    if (not query or query in f"{product.get('name','')} {product.get('colour','')} {product.get('category','')}".lower())
                    and (not self.stock_only.isChecked() or product.get("available", False))]
        sort_index = self.sort_combo.currentIndex()
        if sort_index == 1:
            products.sort(key=lambda item: float(item.get("price_value", 0)))
        elif sort_index == 2:
            products.sort(key=lambda item: float(item.get("price_value", 0)), reverse=True)
        elif sort_index == 3:
            products.sort(key=lambda item: str(item.get("name", "")).lower())

        if not products:
            empty_label = QLabel("No products available in this section.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    color: #cccccc;
                    padding: 80px;
                    border: none;
                    background-color: transparent;
                }
            """)
            self.product_grid.addWidget(empty_label, 0, 0, 1, 2)
            return

        # -------------------------
        # 2 COLUMNS, VERTICAL SCROLL
        # -------------------------
        for index, product in enumerate(products):
            card = self.create_product_card(product)

            row = index // 2
            col = index % 2

            self.product_grid.addWidget(card, row, col)

    def create_product_card(self, product):
        card = ClickableProductCard(product, self.on_product_selected)

        card.setFixedSize(520, 340)
        card.setCursor(Qt.PointingHandCursor)
        card.setObjectName("productCard")

        # Only the full card highlights as one piece
        card.setStyleSheet("""
            QFrame#productCard {
                background-color: #1f1f1f;
                border: 2px solid #333333;
                border-radius: 22px;
            }

            QFrame#productCard:hover {
                background-color: #252525;
                border: 3px solid #2d89ef;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(10)

        # -------------------------
        # PRODUCT IMAGE WITH DISCOUNT BADGE
        # -------------------------
        image_box = QLabel()
        image_box.setFixedSize(475, 225)
        image_box.setAlignment(Qt.AlignCenter)
        image_box.setStyleSheet("""
            QLabel {
                background-color: #333333;
                color: #aaaaaa;
                border-radius: 16px;
                font-size: 18px;
                border: none;
            }
        """)

        image_from_json = (product.get("image", "") 
                           or product.get("image") 
                           or "")
        image_path = self.get_project_root() / image_from_json

        if image_path.exists():
            pixmap = QPixmap(str(image_path))

            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    455,
                    210,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                image_box.setPixmap(pixmap)
            else:
                image_box.setText("Image Error")
        else:
            image_box.setText("No Image")

        # Discount badge stays inside the image area.
        # It does not take extra space, so image/card size remains the same.
        discount_badge = QLabel("", image_box)
        discount_badge.setAlignment(Qt.AlignCenter)
        discount_badge.setFixedSize(120, 32)
        discount_badge.move(340, 10)
        discount_badge.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #ffcc00;
                background-color: rgba(0, 0, 0, 160);
                border-radius: 10px;
                border: none;
            }
        """)

        if not product.get("available", False):
            discount_badge.setText("OUT OF STOCK")
            discount_badge.show()
        elif product.get("discount"):
            discount_badge.setText(product.get("discount_text") or "DISCOUNT")
            discount_badge.show()
        else:
            discount_badge.hide()

        # -------------------------
        # PRODUCT NAME
        # -------------------------
        name = QLabel(product.get("name", "Unnamed Product"))
        name.setAlignment(Qt.AlignCenter)
        name.setWordWrap(True)
        name.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        # -------------------------
        # PRODUCT PRICE
        # -------------------------
        if product.get("discount"):
            original = float(product.get("original_price", 0))
            final = float(product.get("final_price", original))
            price_text = f'<span style="color:#aab3bd; text-decoration:line-through;">£{original:.2f}</span>&nbsp;&nbsp;<span style="color:#00ff99;">£{final:.2f}</span>'
        else:
            price_text = str(product.get("price", "N/A"))
        price = QLabel(price_text)
        price.setTextFormat(Qt.RichText)
        price.setAlignment(Qt.AlignCenter)
        price.setStyleSheet("""
            QLabel {
                font-size: 21px;
                font-weight: bold;
                color: #00ff99;
                background-color: transparent;
                border: none;
            }
        """)

        layout.addWidget(image_box, alignment=Qt.AlignCenter)
        layout.addWidget(name)
        layout.addWidget(price)

        card.setLayout(layout)

        return card

    def clear_products(self):
        while self.product_grid.count():
            item = self.product_grid.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()
