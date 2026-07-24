from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QLineEdit,
    QDialog, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt
from services.discount_service import DiscountService


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
        result = DiscountService.calculate(product.get("price", 0), discount_enabled, product.get("discount_type"), product.get("discount_value"), product.get("discount_price"))
        price_text = f"Original: £{result['original_price']:.2f}"
        if result["active"]:
            price_text += f"\n{result['discount_text']}  →  New: £{result['final_price']:.2f}"
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

        current_price = QLabel(f"Original Price: £{float(product.get('price', 0)):.2f}")
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

        fields = QHBoxLayout()
        amount_column, percentage_column = QVBoxLayout(), QVBoxLayout()
        amount_label, percentage_label = QLabel("Amount off (£)"), QLabel("Percentage off (%)")
        for label in (amount_label, percentage_label):
            label.setStyleSheet("font-size: 15px; color: #c8d0d8; border: none;")
        self.amount_input, self.percentage_input = QLineEdit(), QLineEdit()
        self.amount_input.setPlaceholderText("e.g. 5.00")
        self.percentage_input.setPlaceholderText("e.g. 20")
        input_style = """
            QLineEdit {
                font-size: 17px;
                color: white;
                background-color: #1c2530;
                border: 1px solid #34495e;
                border-radius: 10px;
                padding-left: 12px;
            }
        """
        for field in (self.amount_input, self.percentage_input):
            field.setFixedHeight(55)
            field.setStyleSheet(input_style)
        self.amount_input.textEdited.connect(self.clear_percentage)
        self.percentage_input.textEdited.connect(self.clear_amount)
        self.discount_checkbox.toggled.connect(self.toggle_discount_fields)
        dtype, value = product.get("discount_type"), product.get("discount_value")
        if dtype == "percentage" and value is not None:
            self.percentage_input.setText(str(value))
        elif dtype == "amount" and value is not None:
            self.amount_input.setText(str(value))
        elif product.get("discount") and product.get("discount_price") is not None:
            legacy_amount = float(product.get("price", 0)) - float(product["discount_price"])
            if legacy_amount > 0:
                self.amount_input.setText(f"{legacy_amount:.2f}")
        amount_column.addWidget(amount_label); amount_column.addWidget(self.amount_input)
        percentage_column.addWidget(percentage_label); percentage_column.addWidget(self.percentage_input)
        fields.addLayout(amount_column); fields.addLayout(percentage_column)
        self.amount_label = amount_label
        self.percentage_label = percentage_label

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
        main_layout.addLayout(fields)
        main_layout.addLayout(button_row)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #10151c;")
        self.toggle_discount_fields(self.discount_checkbox.isChecked())

    def handle_save(self):
        try:
            discount_enabled = self.discount_checkbox.isChecked()
            amount_text = self.amount_input.text().strip()
            percentage_text = self.percentage_input.text().strip()
            discount_type = discount_value = discount_price = None
            if discount_enabled:
                if bool(amount_text) == bool(percentage_text):
                    raise ValueError("Enter either an amount or a percentage, not both.")
                original = float(self.product.get("price", 0))
                if amount_text:
                    discount_type, discount_value = "amount", float(amount_text)
                    if discount_value <= 0 or discount_value > original:
                        raise ValueError("Amount must be more than 0 and no more than the original price.")
                else:
                    discount_type, discount_value = "percentage", float(percentage_text)
                    if discount_value <= 0 or discount_value > 100:
                        raise ValueError("Percentage must be between 0 and 100.")
                discount_price = DiscountService.calculate(original, True, discount_type, discount_value)["final_price"]

            self.on_save(
                self.product,
                discount_enabled,
                discount_type, discount_value, discount_price
            )

            self.accept()

        except Exception as error:
            QMessageBox.warning(self, "Discount Error", str(error))

    def clear_percentage(self, text):
        if text:
            self.percentage_input.clear()

    def clear_amount(self, text):
        if text:
            self.amount_input.clear()

    def toggle_discount_fields(self, enabled):
        for widget in (
            self.amount_input, self.percentage_input,
            self.amount_label, self.percentage_label,
        ):
            widget.setEnabled(enabled)
        if not enabled:
            self.amount_input.clear()
            self.percentage_input.clear()
        input_style = """
            QLineEdit {
                font-size: 17px; color: white; background-color: #1c2530;
                border: 1px solid #34495e; border-radius: 10px; padding-left: 12px;
            }
            QLineEdit:disabled {
                color: #68737d; background-color: #151b21;
                border: 1px solid #28323b;
            }
        """
        self.amount_input.setStyleSheet(input_style)
        self.percentage_input.setStyleSheet(input_style)
        label_style = (
            "QLabel { font-size:15px;color:#c8d0d8;border:none; }"
            "QLabel:disabled { color:#59636c; }"
        )
        self.amount_label.setStyleSheet(label_style)
        self.percentage_label.setStyleSheet(label_style)

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
