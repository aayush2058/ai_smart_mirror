from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QLineEdit,
    QDialog, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt


class DiscountManagementScreen(QWidget):
    def __init__(self, on_back, on_update_discount):
        super().__init__()

        self.on_back = on_back
        self.on_update_discount = on_update_discount
        self.products = []

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(45, 35, 45, 35)
        main_layout.setSpacing(20)

        title = QLabel("Discount Management")
        title.setStyleSheet("""
            QLabel {
                font-size: 38px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search discounted products...")
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

        bottom_bar = QHBoxLayout()
        bottom_bar.addWidget(back_button)
        bottom_bar.addStretch()

        main_layout.addWidget(title)
        main_layout.addWidget(self.search_input)
        main_layout.addWidget(self.scroll_area)
        main_layout.addLayout(bottom_bar)

        self.setLayout(main_layout)
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
                str(product.get("price", "")),
                str(product.get("discount_price", "")),
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
            self.list_layout.addWidget(self.create_discount_row(product))

        self.list_layout.addStretch()

    def create_discount_row(self, product):
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

        info = QLabel(
            f"{product.get('name', 'Unnamed Product')}\n"
            f"{product.get('department', 'N/A')} / {product.get('category', 'N/A')}"
        )
        info.setFixedWidth(360)
        info.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        discount_enabled = bool(product.get("discount", False))
        discount_price = product.get("discount_price")

        price_text = f"Price: £{product.get('price', 'N/A')}"
        if discount_enabled and discount_price is not None:
            price_text += f"\nDiscount Price: £{discount_price}"
        else:
            price_text += "\nDiscount: OFF"

        price_label = QLabel(price_text)
        price_label.setStyleSheet("""
            QLabel {
                font-size: 17px;
                color: #dddddd;
                background-color: transparent;
                border: none;
            }
        """)

        status = QLabel("DISCOUNT ON" if discount_enabled else "NO DISCOUNT")
        status.setFixedWidth(170)
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #ffcc00;
                background-color: transparent;
                border: none;
            }
        """)

        edit_button = QPushButton("Edit Discount")
        edit_button.setFixedSize(160, 45)
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
        edit_button.clicked.connect(
            lambda checked=False, p=product: self.open_discount_dialog(p)
        )

        layout.addWidget(info)
        layout.addWidget(price_label)
        layout.addStretch()
        layout.addWidget(status)
        layout.addWidget(edit_button)

        row.setLayout(layout)
        return row

    def open_discount_dialog(self, product):
        dialog = DiscountUpdateDialog(
            product=product,
            on_save=self.on_update_discount
        )
        dialog.exec()

    def clear_products(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


class DiscountUpdateDialog(QDialog):
    def __init__(self, product, on_save):
        super().__init__()

        self.product = product
        self.on_save = on_save

        self.setWindowTitle("Update Discount")
        self.setMinimumWidth(520)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(18)

        title = QLabel(f"Update Discount\n{product.get('name', 'Unnamed Product')}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: white;
            }
        """)

        current_price = QLabel(f"Current Price: £{product.get('price', 'N/A')}")
        current_price.setAlignment(Qt.AlignCenter)
        current_price.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #dddddd;
            }
        """)

        self.discount_checkbox = QCheckBox("Enable Discount")
        self.discount_checkbox.setChecked(bool(product.get("discount", False)))
        self.discount_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 17px;
                color: #dddddd;
                background-color: transparent;
                border: none;
            }
        """)

        self.discount_price_input = QLineEdit()
        self.discount_price_input.setPlaceholderText("Discount price e.g. 9.99")
        self.discount_price_input.setFixedHeight(55)

        if product.get("discount_price") is not None:
            self.discount_price_input.setText(str(product.get("discount_price")))

        self.discount_price_input.setStyleSheet("""
            QLineEdit {
                font-size: 17px;
                color: white;
                background-color: #1c2530;
                border: 1px solid #34495e;
                border-radius: 10px;
                padding-left: 12px;
            }
        """)

        button_row = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(150, 50)
        cancel_button.setStyleSheet(self.grey_button_style())
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton("Save Discount")
        save_button.setFixedSize(180, 50)
        save_button.setStyleSheet(self.green_button_style())
        save_button.clicked.connect(self.handle_save)

        button_row.addStretch()
        button_row.addWidget(cancel_button)
        button_row.addWidget(save_button)

        main_layout.addWidget(title)
        main_layout.addWidget(current_price)
        main_layout.addWidget(self.discount_checkbox)
        main_layout.addWidget(self.discount_price_input)
        main_layout.addLayout(button_row)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #10151c;")

    def handle_save(self):
        try:
            discount_enabled = self.discount_checkbox.isChecked()
            price_text = self.discount_price_input.text().strip()

            discount_price = None
            if discount_enabled:
                if not price_text:
                    raise ValueError("Please enter discount price.")

                discount_price = float(price_text)

                if discount_price < 0:
                    raise ValueError("Discount price cannot be negative.")

            self.on_save(
                self.product,
                discount_enabled,
                discount_price
            )

            self.accept()

        except Exception as error:
            QMessageBox.warning(self, "Discount Error", str(error))

    def green_button_style(self):
        return """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #00a86b;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #007a4d;
            }
        """

    def grey_button_style(self):
        return """
            QPushButton {
                font-size: 16px;
                background-color: #444444;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """