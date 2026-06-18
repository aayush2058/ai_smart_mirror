from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QCheckBox, QFileDialog,
    QFrame, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class ProductFormScreen(QWidget):
    def __init__(self, on_save, on_cancel, on_upload_image):
        super().__init__()

        self.on_save = on_save
        self.on_cancel = on_cancel
        self.on_upload_image = on_upload_image
        self.image_path = ""

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)

        title = QLabel("Add Product")
        title.setStyleSheet("""
            QLabel {
                font-size: 38px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        scroll_container = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        form_card = QFrame()
        form_card.setStyleSheet("""
            QFrame {
                background-color: #1c2530;
                border-radius: 20px;
                border: 1px solid #34404d;
            }
        """)

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(35, 30, 35, 30)
        form_layout.setSpacing(22)

        self.product_code_input = self.create_input("Product code / SKU")
        self.name_input = self.create_input("Product name")
        self.price_input = self.create_input("Price e.g. 12.99")
        self.colour_input = self.create_input("Colour")
        self.location_input = self.create_input("Store location")
        self.sizes_input = self.create_input("Sizes e.g. S:5, M:4, L:2")
        self.discount_price_input = self.create_input("Discount price optional")

        self.department_combo = QComboBox()
        self.department_combo.addItems(["Men", "Women", "Kids", "Decors", "Accessories"])
        self.style_combo(self.department_combo)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["Upper Fit", "Lower Fit", "Footwear", "Accessories", "Miscellaneous"])
        self.style_combo(self.category_combo)

        self.tryon_category_combo = QComboBox()
        self.tryon_category_combo.addItems(["None", "Shirts", "Pants"])
        self.style_combo(self.tryon_category_combo)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Product description")
        self.description_input.setFixedHeight(100)
        self.description_input.setStyleSheet("""
            QTextEdit {
                font-size: 17px;
                color: white;
                background-color: #10151c;
                border: 1px solid #34495e;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        self.available_checkbox = self.create_checkbox("Available")
        self.available_checkbox.setChecked(True)

        self.discount_checkbox = self.create_checkbox("Discount")
        self.tryon_enabled_checkbox = self.create_checkbox("Enable Virtual Try-On")

        self.width_input = self.create_input("Try-on width scale e.g. 2.0")
        self.height_input = self.create_input("Try-on height scale e.g. 1.3")
        self.vertical_input = self.create_input("Vertical offset e.g. 0.16")
        self.horizontal_input = self.create_input("Horizontal offset e.g. 5")

        self.image_preview = QLabel("No Image Selected")
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setFixedSize(180, 180)
        self.image_preview.setStyleSheet("""
            QLabel {
                background-color: #10151c;
                color: #cccccc;
                border: 1px solid #34495e;
                border-radius: 12px;
                font-size: 16px;
            }
        """)

        upload_button = QPushButton("Upload Image")
        upload_button.setFixedSize(180, 52)
        upload_button.setStyleSheet(self.blue_button_style())
        upload_button.clicked.connect(self.handle_upload_image)

        image_row = QHBoxLayout()
        image_row.addWidget(self.image_preview)
        image_row.addWidget(upload_button)
        image_row.addStretch()

        button_row = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(170, 55)
        cancel_button.setStyleSheet(self.grey_button_style())
        cancel_button.clicked.connect(self.on_cancel)

        save_button = QPushButton("Save Product")
        save_button.setFixedSize(190, 55)
        save_button.setStyleSheet(self.green_button_style())
        save_button.clicked.connect(self.handle_save)

        button_row.addStretch()
        button_row.addWidget(cancel_button)
        button_row.addWidget(save_button)

        form_layout.addWidget(self.product_code_input)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.department_combo)
        form_layout.addWidget(self.category_combo)
        form_layout.addWidget(self.price_input)
        form_layout.addWidget(self.colour_input)
        form_layout.addWidget(self.location_input)
        form_layout.addWidget(self.description_input)
        form_layout.addWidget(self.sizes_input)
        form_layout.addWidget(self.available_checkbox)
        form_layout.addWidget(self.discount_checkbox)
        form_layout.addWidget(self.discount_price_input)
        form_layout.addWidget(self.tryon_enabled_checkbox)
        form_layout.addWidget(self.tryon_category_combo)
        form_layout.addWidget(self.width_input)
        form_layout.addWidget(self.height_input)
        form_layout.addWidget(self.vertical_input)
        form_layout.addWidget(self.horizontal_input)
        form_layout.addLayout(image_row)
        form_layout.addLayout(button_row)

        form_card.setLayout(form_layout)
        scroll_layout.addWidget(form_card)
        scroll_container.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_container)

        main_layout.addWidget(title)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #10151c;")

    def create_input(self, placeholder):
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setFixedHeight(55)
        field.setStyleSheet("""
            QLineEdit {
                font-size: 17px;
                color: white;
                background-color: #10151c;
                border: 1px solid #34495e;
                border-radius: 10px;
                padding-left: 12px;
                padding-right: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #2d89ef;
            }
        """)
        return field

    def create_checkbox(self, text):
        checkbox = QCheckBox(text)
        checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 17px;
                color: #dddddd;
                background-color: transparent;
                border: none;
            }
        """)
        return checkbox

    def style_combo(self, combo):
        combo.setFixedHeight(55)
        combo.setStyleSheet("""
            QComboBox {
                font-size: 17px;
                color: white;
                background-color: #10151c;
                border: 1px solid #34495e;
                border-radius: 10px;
                padding-left: 12px;
            }
        """)

    def handle_upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Product Image",
            "",
            "Images (*.png *.jpg *.jpeg *.webp)"
        )

        if not file_path:
            return

        try:
            tryon_category = self.tryon_category_combo.currentText()
            saved_path = self.on_upload_image(file_path, tryon_category)
            self.image_path = saved_path

            pixmap = QPixmap(saved_path)
            if not pixmap.isNull():
                self.image_preview.setPixmap(
                    pixmap.scaled(170, 170, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
            else:
                self.image_preview.setText("Image Saved")

        except Exception as error:
            QMessageBox.warning(self, "Image Error", str(error))

    def handle_save(self):
        try:
            product_data = self.collect_product_data()
            self.on_save(product_data)
        except Exception as error:
            QMessageBox.warning(self, "Product Error", str(error))

    def collect_product_data(self):
        tryon_category = self.tryon_category_combo.currentText()

        if tryon_category == "None":
            tryon_category = None

        discount_price = self.discount_price_input.text().strip()
        discount_price = float(discount_price) if discount_price else None

        return {
            "product_code": self.product_code_input.text().strip(),
            "name": self.name_input.text().strip(),
            "department": self.department_combo.currentText(),
            "category": self.category_combo.currentText(),
            "price": float(self.price_input.text().strip()),
            "colour": self.colour_input.text().strip(),
            "description": self.description_input.toPlainText().strip(),
            "image_path": self.image_path,
            "available": self.available_checkbox.isChecked(),
            "discount": self.discount_checkbox.isChecked(),
            "discount_price": discount_price,
            "location": self.location_input.text().strip(),
            "tryon_enabled": self.tryon_enabled_checkbox.isChecked(),
            "tryon_category": tryon_category,
            "sizes": self.parse_sizes(),
            "width_scale": float(self.width_input.text().strip() or 1.0),
            "height_scale": float(self.height_input.text().strip() or 1.0),
            "vertical_offset": float(self.vertical_input.text().strip() or 0.0),
            "horizontal_offset": int(self.horizontal_input.text().strip() or 0),
        }

    def parse_sizes(self):
        text = self.sizes_input.text().strip()

        if not text:
            return []

        result = []

        for item in text.split(","):
            if ":" in item:
                size, quantity = item.split(":", 1)
                result.append({
                    "size": size.strip(),
                    "quantity": int(quantity.strip())
                })

        return result

    def clear_form(self):
        self.product_code_input.clear()
        self.name_input.clear()
        self.price_input.clear()
        self.colour_input.clear()
        self.location_input.clear()
        self.description_input.clear()
        self.sizes_input.clear()
        self.discount_price_input.clear()
        self.width_input.clear()
        self.height_input.clear()
        self.vertical_input.clear()
        self.horizontal_input.clear()

        self.available_checkbox.setChecked(True)
        self.discount_checkbox.setChecked(False)
        self.tryon_enabled_checkbox.setChecked(False)

        self.department_combo.setCurrentIndex(0)
        self.category_combo.setCurrentIndex(0)
        self.tryon_category_combo.setCurrentIndex(0)

        self.image_path = ""
        self.image_preview.clear()
        self.image_preview.setText("No Image Selected")

    def blue_button_style(self):
        return """
            QPushButton {
                font-size: 17px;
                background-color: #2d89ef;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #1b5fbd;
            }
        """

    def green_button_style(self):
        return """
            QPushButton {
                font-size: 17px;
                font-weight: bold;
                background-color: #00a86b;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #007a4d;
            }
        """

    def grey_button_style(self):
        return """
            QPushButton {
                font-size: 17px;
                background-color: #444444;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """