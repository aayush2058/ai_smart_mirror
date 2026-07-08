from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QMessageBox

class InventoryManagementScreen(QWidget):
    def __init__(self, on_back, on_update_stock):
        super().__init__()

        self.on_back = on_back
        self.on_update_stock = on_update_stock
        self.products = []

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(45, 35, 45, 35)
        main_layout.setSpacing(20)

        top_bar = QHBoxLayout()

        title = QLabel("Stock & Sizes")
        title.setStyleSheet("""
            QLabel {
                font-size: 38px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        top_bar.addWidget(title)
        top_bar.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search product stock...")
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

        main_layout.addLayout(top_bar)
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
                str(product.get("colour", "")),
                str(product.get("location", "")),
            ]).lower()

            if query in search_text:
                filtered.append(product)

        self.render_products(filtered)

    def render_products(self, products):
        self.clear_products()

        if not products:
            empty_label = QLabel("No inventory products found.")
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
            self.list_layout.addWidget(self.create_inventory_row(product))

        self.list_layout.addStretch()

    def create_inventory_row(self, product):
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

        name = QLabel(
            f"{product.get('name', 'Unnamed Product')}\n"
            f"{product.get('department', 'N/A')} / {product.get('category', 'N/A')}"
        )
        name.setFixedWidth(340)
        name.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        sizes_text = self.get_sizes_text(product)
        sizes = QLabel(sizes_text)
        sizes.setStyleSheet("""
            QLabel {
                font-size: 17px;
                color: #dddddd;
                background-color: transparent;
                border: none;
            }
        """)

        status = QLabel(self.get_stock_status(product))
        status.setFixedWidth(150)
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

        update_button = QPushButton("Update")
        update_button.setFixedSize(110, 45)
        update_button.setStyleSheet("""
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
        update_button.clicked.connect(
            lambda checked=False, p=product: self.open_stock_dialog(p)
        )

        layout.addWidget(name)
        layout.addWidget(sizes)
        layout.addStretch()
        layout.addWidget(status)
        layout.addWidget(update_button)

        row.setLayout(layout)
        return row

    def get_sizes_text(self, product):
        sizes = product.get("sizes", [])

        if not sizes:
            return "No sizes set"

        parts = []

        for item in sizes:
            size = item.get("size", "N/A")
            quantity = item.get("quantity", 0)
            parts.append(f"{size}: {quantity}")

        return " | ".join(parts)

    def get_stock_status(self, product):
        sizes = product.get("sizes", [])

        if not sizes:
            return "NO STOCK"

        total = sum(int(item.get("quantity", 0)) for item in sizes)

        if total == 0:
            return "OUT"

        if total <= 3:
            return "LOW"

        return "AVAILABLE"

    def clear_products(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

    def open_stock_dialog(self, product):
        dialog = StockUpdateDialog(
            product=product,
            on_save=self.on_update_stock
        )

        dialog.exec()


class StockUpdateDialog(QDialog):
    def __init__(self, product, on_save):
        super().__init__()

        self.product = product
        self.on_save = on_save
        self.size_inputs = []

        self.setWindowTitle("Update Stock")
        self.setMinimumWidth(500)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(18)

        title = QLabel(f"Update Stock\n{product.get('name', 'Unnamed Product')}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: white;
            }
        """)

        main_layout.addWidget(title)

        sizes = product.get("sizes", [])

        if not sizes:
            sizes = [
                {"size": "S", "quantity": 0},
                {"size": "M", "quantity": 0},
                {"size": "L", "quantity": 0}
            ]

        for item in sizes:
            row = QHBoxLayout()

            size_input = QLineEdit(str(item.get("size", "")))
            size_input.setFixedHeight(45)
            size_input.setPlaceholderText("Size")

            quantity_input = QLineEdit(str(item.get("quantity", 0)))
            quantity_input.setFixedHeight(45)
            quantity_input.setPlaceholderText("Quantity")

            size_input.setStyleSheet(self.input_style())
            quantity_input.setStyleSheet(self.input_style())

            row.addWidget(QLabel("Size:"))
            row.addWidget(size_input)
            row.addWidget(QLabel("Qty:"))
            row.addWidget(quantity_input)

            main_layout.addLayout(row)

            self.size_inputs.append((size_input, quantity_input))

        add_row_button = QPushButton("+ Add Size")
        add_row_button.setFixedHeight(45)
        add_row_button.setStyleSheet(self.blue_button_style())
        add_row_button.clicked.connect(self.add_size_row)

        button_row = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(150, 50)
        cancel_button.setStyleSheet(self.grey_button_style())
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton("Save Stock")
        save_button.setFixedSize(170, 50)
        save_button.setStyleSheet(self.green_button_style())
        save_button.clicked.connect(self.handle_save)

        button_row.addStretch()
        button_row.addWidget(cancel_button)
        button_row.addWidget(save_button)

        main_layout.addWidget(add_row_button)
        main_layout.addLayout(button_row)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #10151c;")

    def add_size_row(self):
        row = QHBoxLayout()

        size_input = QLineEdit()
        size_input.setFixedHeight(45)
        size_input.setPlaceholderText("Size")

        quantity_input = QLineEdit()
        quantity_input.setFixedHeight(45)
        quantity_input.setPlaceholderText("Quantity")

        size_input.setStyleSheet(self.input_style())
        quantity_input.setStyleSheet(self.input_style())

        row.addWidget(QLabel("Size:"))
        row.addWidget(size_input)
        row.addWidget(QLabel("Qty:"))
        row.addWidget(quantity_input)

        # Insert before Add Size button and button row
        self.layout().insertLayout(self.layout().count() - 2, row)

        self.size_inputs.append((size_input, quantity_input))

    def handle_save(self):
        try:
            sizes = []

            for size_input, quantity_input in self.size_inputs:
                size = size_input.text().strip()
                quantity_text = quantity_input.text().strip()

                if not size:
                    continue

                quantity = int(quantity_text or 0)

                if quantity < 0:
                    raise ValueError("Quantity cannot be negative.")

                sizes.append({
                    "size": size,
                    "quantity": quantity
                })

            if not sizes:
                raise ValueError("Please enter at least one size.")

            self.on_save(self.product, sizes)
            self.accept()

        except Exception as error:
            QMessageBox.warning(self, "Stock Error", str(error))

    def input_style(self):
        return """
            QLineEdit {
                font-size: 16px;
                color: white;
                background-color: #1c2530;
                border: 1px solid #34495e;
                border-radius: 8px;
                padding-left: 10px;
            }
        """

    def blue_button_style(self):
        return """
            QPushButton {
                font-size: 16px;
                background-color: #2d89ef;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #1b5fbd;
            }
        """

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