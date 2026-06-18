from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from pathlib import Path

class ProductManagementScreen(QWidget):
    def __init__(self, on_back, on_add_product, on_edit_product, on_delete_product):
        super().__init__()

        self.on_back = on_back
        self.on_add_product = on_add_product
        self.on_edit_product = on_edit_product
        self.on_delete_product = on_delete_product

        self.products = []

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(45, 35, 45, 35)
        self.main_layout.setSpacing(20)

        top_bar = QHBoxLayout()

        title = QLabel("Manage Products")
        title.setStyleSheet("""
            QLabel {
                font-size: 38px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        add_button = QPushButton("+ Add Product")
        add_button.setFixedSize(190, 55)
        add_button.setStyleSheet("""
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
        add_button.clicked.connect(self.on_add_product)

        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(add_button)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products by name, category, colour or location...")
        self.search_input.setFixedHeight(52)
        self.search_input.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                color: white;
                background-color: #1f2b38;
                border: 1px solid #34495e;
                border-radius: 12px;
                padding-left: 16px;
                padding-right: 16px;
            }
            QLineEdit:focus {
                border: 2px solid #2d89ef;
            }
        """)
        self.search_input.textChanged.connect(self.filter_products)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #10151c;
                border: none;
            }
        """)

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(14)
        self.list_layout.setContentsMargins(5, 5, 5, 5)

        self.list_container.setLayout(self.list_layout)
        self.scroll_area.setWidget(self.list_container)

        bottom_bar = QHBoxLayout()

        back_button = QPushButton("Back")
        back_button.setFixedSize(170, 55)
        back_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                background-color: #444444;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        back_button.clicked.connect(self.on_back)

        bottom_bar.addWidget(back_button)
        bottom_bar.addStretch()

        self.main_layout.addLayout(top_bar)
        self.main_layout.addWidget(self.search_input)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addLayout(bottom_bar)

        self.setLayout(self.main_layout)
        self.setStyleSheet("background-color: #10151c;")

    def set_products(self, products):
        self.products = products
        self.render_products(products)

    def filter_products(self):
        query = self.search_input.text().strip().lower()

        if not query:
            self.render_products(self.products)
            return

        filtered = []

        for product in self.products:
            search_text = " ".join([
                str(product.get("name", "")),
                str(product.get("department", "")),
                str(product.get("category", "")),
                str(product.get("colour", "")),
                str(product.get("location", "")),
            ]).lower()

            if query in search_text:
                filtered.append(product)

        self.render_products(filtered)

    def render_products(self, products):
        self.clear_products()

        if not products:
            empty_label = QLabel("No products found.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    font-size: 22px;
                    color: #cccccc;
                    background-color: transparent;
                    border: none;
                    padding: 60px;
                }
            """)
            self.list_layout.addWidget(empty_label)
            self.list_layout.addStretch()
            return

        for product in products:
            self.list_layout.addWidget(self.create_product_row(product))

        self.list_layout.addStretch()

    def create_product_row(self, product):
        row = QFrame()
        row.setStyleSheet("""
            QFrame {
                background-color: #1c2530;
                border-radius: 16px;
                border: 1px solid #34404d;
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(20)

        image_label = QLabel()
        image_label.setFixedSize(80, 80)

        image_path = product.get("image", "")

        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            image_label.setPixmap(
                pixmap.scaled(
                    80,
                    80,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )
        else:
            image_label.setText("No\nImage")
            image_label.setAlignment(Qt.AlignCenter)

        info = QLabel(
            f"{product.get('name', 'Unnamed Product')}\n"
            f"{product.get('department', 'N/A')} / {product.get('category', 'N/A')}  |  "
            f"{product.get('price', 'N/A')}  |  {product.get('colour', 'N/A')}"
        )
        info.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        status = QLabel(self.get_status_text(product))
        status.setFixedWidth(180)
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #00ff99;
                background-color: transparent;
                border: none;
            }
        """)

        edit_button = QPushButton("Edit")
        edit_button.setFixedSize(100, 45)
        edit_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                background-color: #2d89ef;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #1b5fbd;
            }
        """)
        edit_button.clicked.connect(lambda checked=False, p=product: self.on_edit_product(p))

        delete_button = QPushButton("Delete")
        delete_button.setFixedSize(100, 45)
        delete_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                background-color: #8b2d2d;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #b13b3b;
            }
        """)
        delete_button.clicked.connect(lambda checked=False, p=product: self.on_delete_product(p))

        layout.addWidget(image_label)
        layout.addWidget(info)
        layout.addStretch()
        layout.addWidget(status)
        layout.addWidget(edit_button)
        layout.addWidget(delete_button)

        row.setLayout(layout)
        return row

    def get_status_text(self, product):
        if product.get("discount", False):
            return "DISCOUNT"

        if product.get("available", False):
            return "AVAILABLE"

        return "OUT OF STOCK"

    def clear_products(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()