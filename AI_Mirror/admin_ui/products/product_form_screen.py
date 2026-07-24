from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QCheckBox, QFileDialog,
    QFrame, QMessageBox, QScrollArea, QDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from paths import resolve_project_path

class ProductFormScreen(QWidget):
    def __init__(self, on_save, on_cancel, on_upload_image):
        super().__init__()

        self.on_save = on_save
        self.on_cancel = on_cancel
        self.on_upload_image = on_upload_image
        self.image_path = ""
        self.editing_product_id = None

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)

        self.title = QLabel("Add Product")
        self.title.setStyleSheet("""
            QLabel {
                font-size: 38px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        self.mode_notice = QLabel("")
        self.mode_notice.setWordWrap(True)
        self.mode_notice.setStyleSheet(
            "font-size:17px;color:#ffd27a;background:#302817;padding:12px;"
            "border:1px solid #705a25;border-radius:10px;"
        )
        self.mode_notice.hide()

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
        self.colour_input = self.create_editable_combo(
            "Select or type colour", ["Black", "White", "Navy", "Blue", "Red", "Green", "Grey", "Pink", "Beige", "Brown"]
        )
        self.location_input = self.create_editable_combo(
            "Select or type store location", ["Ground Floor", "First Floor", "Men's Section", "Women's Section", "Kids Section", "Accessories", "Front Display"]
        )
        self.sizes_input = self.create_editable_combo(
            "Select a size template or type quantities",
            ["XS:0, S:0, M:0, L:0, XL:0", "S:0, M:0, L:0", "28:0, 30:0, 32:0, 34:0, 36:0", "One Size:0"]
        )

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
        self.discount_checkbox.toggled.connect(self.toggle_discount_options)
        self.discount_amount_input = self.create_input("Amount off (£), e.g. 5.00")
        self.discount_percentage_input = self.create_input("Percentage off (%), e.g. 20")
        self.discount_amount_input.textEdited.connect(self.clear_discount_percentage)
        self.discount_percentage_input.textEdited.connect(self.clear_discount_amount)
        self.discount_options = QFrame()
        discount_layout = QHBoxLayout(self.discount_options)
        discount_layout.setContentsMargins(0, 0, 0, 0)
        discount_layout.addWidget(self.discount_amount_input)
        discount_layout.addWidget(self.discount_percentage_input)
        self.discount_options.setStyleSheet("QFrame { background: transparent; border: none; }")
        self.toggle_discount_options(False)
        self.tryon_enabled_checkbox = self.create_checkbox("Enable Virtual Try-On")

        self.width_input = self.create_editable_combo("Try-on width scale", ["1.0", "1.2", "1.5", "2.0"])
        self.height_input = self.create_editable_combo("Try-on height scale", ["1.0", "1.2", "1.3", "1.5"])
        self.vertical_input = self.create_editable_combo("Vertical offset", ["0.0", "0.05", "0.10", "0.16", "0.20"])
        self.horizontal_input = self.create_editable_combo("Horizontal offset", ["0", "-10", "-5", "5", "10"])

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

        self.upload_button = QPushButton("Upload Image")
        self.upload_button.setFixedSize(180, 52)
        self.upload_button.setStyleSheet(self.blue_button_style())
        self.upload_button.clicked.connect(self.handle_upload_image)

        image_row = QHBoxLayout()
        image_row.addWidget(self.image_preview)
        image_row.addWidget(self.upload_button)
        image_row.addStretch()

        button_row = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(170, 55)
        cancel_button.setStyleSheet(self.grey_button_style())
        cancel_button.clicked.connect(self.on_cancel)

        self.save_button = QPushButton("Save Product")
        self.save_button.setFixedSize(190, 55)
        self.save_button.setStyleSheet(self.green_button_style())
        self.save_button.clicked.connect(self.handle_save)

        preview_button = QPushButton("Preview as Customer")
        preview_button.setFixedSize(210, 55)
        preview_button.setStyleSheet(self.blue_button_style())
        preview_button.clicked.connect(self.preview_as_customer)

        button_row.addStretch()
        button_row.addWidget(preview_button)
        button_row.addWidget(cancel_button)
        button_row.addWidget(self.save_button)

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
        form_layout.addWidget(self.discount_options)
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

        main_layout.addWidget(self.title)
        main_layout.addWidget(self.mode_notice)
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
            QLineEdit:disabled {
                color: #68737d;
                background-color: #151b21;
                border: 1px solid #28323b;
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

    def create_editable_combo(self, placeholder, values):
        combo = QComboBox()
        combo.setEditable(True)
        combo.addItem("")
        combo.addItems(values)
        combo.lineEdit().setPlaceholderText(placeholder)
        self.style_combo(combo)
        return combo

    def toggle_discount_options(self, enabled):
        self.discount_options.setVisible(True)
        self.discount_amount_input.setEnabled(enabled)
        self.discount_percentage_input.setEnabled(enabled)
        if not enabled:
            self.discount_amount_input.clear()
            self.discount_percentage_input.clear()

    def clear_discount_percentage(self, text):
        if text:
            self.discount_percentage_input.clear()

    def clear_discount_amount(self, text):
        if text:
            self.discount_amount_input.clear()

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

            full_path = resolve_project_path(saved_path)
            pixmap = QPixmap(str(full_path)) if full_path else QPixmap()
            
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

        product_code = self.product_code_input.text().strip()
        name = self.name_input.text().strip()
        price_text = self.price_input.text().strip()
        if not product_code:
            raise ValueError("Product code / SKU is required.")
        if not name:
            raise ValueError("Product name is required.")
        if not price_text:
            raise ValueError("Product price is required.")
        price = float(price_text)
        if price <= 0:
            raise ValueError("Product price must be greater than zero.")
        if self.tryon_enabled_checkbox.isChecked() and (not self.image_path or tryon_category is None):
            raise ValueError("Virtual try-on needs a product image and Shirts or Pants category.")

        discount_enabled = self.discount_checkbox.isChecked()
        amount_text = self.discount_amount_input.text().strip()
        percentage_text = self.discount_percentage_input.text().strip()
        discount_type = discount_value = discount_price = None
        if discount_enabled:
            if bool(amount_text) == bool(percentage_text):
                raise ValueError("Enter either an amount off or a percentage off, not both.")
            if amount_text:
                discount_type, discount_value = "amount", float(amount_text)
                if discount_value <= 0 or discount_value > price:
                    raise ValueError("Discount amount must be more than £0 and no more than the price.")
                discount_price = round(price - discount_value, 2)
            else:
                discount_type, discount_value = "percentage", float(percentage_text)
                if discount_value <= 0 or discount_value > 100:
                    raise ValueError("Discount percentage must be between 0 and 100.")
                discount_price = round(price * (1 - discount_value / 100), 2)

        return {
            "product_code": product_code,
            "name": name,
            "department": self.department_combo.currentText(),
            "category": self.category_combo.currentText(),
            "price": price,
            "colour": self.colour_input.currentText().strip(),
            "description": self.description_input.toPlainText().strip(),
            "image_path": self.image_path,
            "available": self.available_checkbox.isChecked(),
            "discount": discount_enabled,
            "discount_price": discount_price,
            "discount_type": discount_type,
            "discount_value": discount_value,
            "location": self.location_input.currentText().strip(),
            "tryon_enabled": self.tryon_enabled_checkbox.isChecked(),
            "tryon_category": tryon_category,
            "sizes": self.parse_sizes(),
            "width_scale": float(self.width_input.currentText().strip() or 1.0),
            "height_scale": float(self.height_input.currentText().strip() or 1.0),
            "vertical_offset": float(self.vertical_input.currentText().strip() or 0.0),
            "horizontal_offset": int(self.horizontal_input.currentText().strip() or 0),
        }

    def parse_sizes(self):
        text = self.sizes_input.currentText().strip()

        if not text:
            return []

        result = []

        for item in text.split(","):
            if ":" in item:
                size, quantity = item.split(":", 1)
                quantity_value = int(quantity.strip())
                if quantity_value < 0:
                    raise ValueError("Stock quantities cannot be negative.")
                if any(existing["size"].lower() == size.strip().lower() for existing in result):
                    raise ValueError(f"Size {size.strip()} is entered more than once.")
                result.append({
                    "size": size.strip(),
                    "quantity": quantity_value
                })
            else:
                raise ValueError("Use Size:Quantity format, for example S:5, M:3.")

        return result

    def preview_as_customer(self):
        try:
            product = self.collect_product_data()
        except Exception as error:
            QMessageBox.warning(self, "Preview Needs Valid Details", str(error)); return
        dialog = QDialog(self); dialog.setWindowTitle("Customer Product Preview"); dialog.setMinimumSize(650, 500)
        layout = QVBoxLayout(dialog)
        heading = QLabel("CUSTOMER PREVIEW"); heading.setAlignment(Qt.AlignCenter)
        heading.setStyleSheet("font-size:16px;color:#8fa0b0;")
        image = QLabel("No product image"); image.setAlignment(Qt.AlignCenter); image.setFixedHeight(250)
        full_path = resolve_project_path(product.get("image_path"))
        if full_path and full_path.exists():
            pixmap = QPixmap(str(full_path))
            image.setPixmap(pixmap.scaled(420, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        price_text = f'£{product["price"]:.2f}'
        if product.get("discount") and product.get("discount_price") is not None:
            price_text = f'<span style="text-decoration:line-through;color:#9ba5af;">£{product["price"]:.2f}</span> &nbsp; <span style="color:#00d98b;">£{product["discount_price"]:.2f}</span>'
        details = QLabel(f'<h1>{product["name"]}</h1><h2>{price_text}</h2><p>{product["description"] or "No description"}</p><p>Colour: {product["colour"] or "Not specified"}<br>Location: {product["location"] or "Not assigned"}</p>')
        details.setTextFormat(Qt.RichText); details.setWordWrap(True); details.setStyleSheet("color:white;font-size:17px;")
        close = QPushButton("Close Preview"); close.setFixedHeight(48); close.clicked.connect(dialog.accept)
        layout.addWidget(heading); layout.addWidget(image); layout.addWidget(details); layout.addWidget(close)
        dialog.setStyleSheet("background:#151c24; QPushButton{background:#2d89ef;color:white;border-radius:10px;font-size:17px;}")
        dialog.exec()

    def clear_form(self):
        self.product_code_input.clear()
        self.name_input.clear()
        self.price_input.clear()
        self.colour_input.setCurrentIndex(0)
        self.location_input.setCurrentIndex(0)
        self.description_input.clear()
        self.sizes_input.setCurrentIndex(0)
        self.discount_amount_input.clear()
        self.discount_percentage_input.clear()
        self.width_input.setCurrentIndex(0)
        self.height_input.setCurrentIndex(0)
        self.vertical_input.setCurrentIndex(0)
        self.horizontal_input.setCurrentIndex(0)

        self.available_checkbox.setChecked(True)
        self.discount_checkbox.setChecked(False)
        self.tryon_enabled_checkbox.setChecked(False)

        self.department_combo.setCurrentIndex(0)
        self.category_combo.setCurrentIndex(0)
        self.tryon_category_combo.setCurrentIndex(0)

        self.image_path = ""
        self.image_preview.clear()
        self.image_preview.setText("No Image Selected")
        self.upload_button.setText("Upload Image")

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
    
    def set_add_mode(self):
        self.editing_product_id = None
        self.clear_form()
        self.title.setText("Add Product")
        self.mode_notice.hide()
        self.save_button.setText("Save Product")
        self.upload_button.setText("Upload Image")

    def set_edit_mode(self, product):
        
        self.clear_form()

        self.editing_product_id = product.get("id")
        product_name = str(product.get("name", "Product"))
        self.title.setText(f"Edit Product — {product_name}")
        self.mode_notice.setText(
            "Saving will update this product"
        )
        self.mode_notice.show()
        self.save_button.setText("Save Changes")

        self.product_code_input.setText(str(product.get("product_code", "")))
        self.name_input.setText(str(product.get("name", "")))
        self.price_input.setText(str(product.get("price", "")))
        self.colour_input.setCurrentText(str(product.get("colour", "")))
        self.location_input.setCurrentText(str(product.get("location", "")))
        self.description_input.setPlainText(str(product.get("description", "")))

        self.available_checkbox.setChecked(bool(product.get("available", True)))
        self.discount_checkbox.setChecked(bool(product.get("discount", False)))
        self.tryon_enabled_checkbox.setChecked(bool(product.get("tryon_enabled", False)))

        discount_type = product.get("discount_type")
        discount_value = product.get("discount_value")
        if discount_type == "percentage" and discount_value is not None:
            self.discount_percentage_input.setText(str(discount_value))
        elif discount_type == "amount" and discount_value is not None:
            self.discount_amount_input.setText(str(discount_value))
        elif product.get("discount_price") is not None:
            legacy_amount = float(product.get("price", 0)) - float(product.get("discount_price"))
            if legacy_amount > 0:
                self.discount_amount_input.setText(f"{legacy_amount:.2f}")

        self.image_path = product.get("image_path") or product.get("image") or ""
        self.load_image_preview(self.image_path)
        self.upload_button.setText("Change Image")

        self.set_combo_value(self.department_combo, product.get("department", "Men"))
        self.set_combo_value(self.category_combo, product.get("category", "Upper Fit"))

        tryon_category = product.get("tryon_category") or "None"
        self.set_combo_value(self.tryon_category_combo, tryon_category)

        tryon_settings = product.get("tryon_settings") or {}

        sizes = product.get("sizes", [])
        self.sizes_input.setCurrentText(", ".join(
            f'{item.get("size")}:{item.get("quantity", 0)}' for item in sizes if item.get("size")
        ))

        self.width_input.setCurrentText(str(tryon_settings.get("width_scale", product.get("width_scale", ""))))
        self.height_input.setCurrentText(str(tryon_settings.get("height_scale", product.get("height_scale", ""))))
        self.vertical_input.setCurrentText(str(tryon_settings.get("vertical_offset", product.get("vertical_offset", ""))))
        self.horizontal_input.setCurrentText(str(tryon_settings.get("horizontal_offset", product.get("horizontal_offset", ""))))


    def set_combo_value(self, combo, value):
        index = combo.findText(str(value))

        if index >= 0:
            combo.setCurrentIndex(index)

    def load_image_preview(self, image_path):
        if not image_path:
            self.image_preview.clear()
            self.image_preview.setText("No Image Selected")
            return

        full_path = resolve_project_path(image_path)

        if full_path and full_path.exists():
            pixmap = QPixmap(str(full_path))

            if not pixmap.isNull():
                self.image_preview.setPixmap(
                    pixmap.scaled(
                        170,
                        170,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )
                return

        self.image_preview.clear()
        self.image_preview.setText("Image Not Found")
