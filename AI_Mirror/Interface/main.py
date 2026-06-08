import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from product_catalog import ProductCatalog

from ui.welcome_screen import WelcomeScreen
from ui.department_screen import DepartmentScreen
from ui.category_screen import CategoryScreen
from ui.catalogue_screen import CatalogueScreen
from ui.product_detail_screen import ProductDetailScreen


class SmartMirrorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Smart Mirror")
        self.setMinimumSize(1200, 800)

        self.selected_department = None
        self.selected_category = None
        self.selected_product = None

        self.catalog = ProductCatalog()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.welcome_screen = WelcomeScreen(
            on_start=self.go_to_department_screen
        )

        self.department_screen = DepartmentScreen(
            on_department_selected=self.go_to_category_screen,
            on_back=self.go_to_welcome_screen
        )

        self.category_screen = CategoryScreen(
            on_category_selected=self.go_to_catalogue_screen,
            on_back=self.go_to_department_screen
        )

        self.catalogue_screen = CatalogueScreen(
            on_product_selected=self.go_to_product_detail_screen,
            on_back=self.go_to_category_screen_from_catalogue,
            on_map=self.go_to_map_screen
        )

        self.product_detail_screen = ProductDetailScreen(
            on_back=self.go_back_to_catalogue,
            on_try_on=self.go_to_camera_warning_screen,
            on_map=self.go_to_map_screen
        )

        self.stack.addWidget(self.welcome_screen)
        self.stack.addWidget(self.department_screen)
        self.stack.addWidget(self.category_screen)
        self.stack.addWidget(self.catalogue_screen)
        self.stack.addWidget(self.product_detail_screen)

        self.stack.setCurrentWidget(self.welcome_screen)

    def go_to_welcome_screen(self):
        self.stack.setCurrentWidget(self.welcome_screen)

    def go_to_department_screen(self):
        self.stack.setCurrentWidget(self.department_screen)

    def go_to_category_screen(self, department):
        self.selected_department = department
        self.category_screen.set_department(department)
        self.stack.setCurrentWidget(self.category_screen)

    def go_to_category_screen_from_catalogue(self):
        self.stack.setCurrentWidget(self.category_screen)

    def go_to_catalogue_screen(self, category):
        self.selected_category = category

        products = self.catalog.get_products(
            department=self.selected_department,
            category=self.selected_category
        )

        self.catalogue_screen.set_products(
            self.selected_department,
            self.selected_category,
            products
        )

        self.stack.setCurrentWidget(self.catalogue_screen)

    def go_to_product_detail_screen(self, product):
        self.selected_product = product
        self.product_detail_screen.set_product(product)
        self.stack.setCurrentWidget(self.product_detail_screen)

    def go_back_to_catalogue(self):
        self.stack.setCurrentWidget(self.catalogue_screen)

    def go_to_camera_warning_screen(self, product):
        self.selected_product = product
        print(f"Virtual Try On selected for: {product.get('name')}")

    def go_to_map_screen(self):
        print("Map button clicked")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = SmartMirrorApp()
    window.show()

    sys.exit(app.exec())