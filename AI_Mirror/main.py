import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from services.product_service import ProductCatalog
from ui.tryon_screen import TryOnScreen
from ui.welcome_screen import WelcomeScreen
from ui.department_screen import DepartmentScreen
from ui.category_screen import CategoryScreen
from ui.catalogue_screen import CatalogueScreen
from ui.product_detail_screen import ProductDetailScreen
from ui.camera_warning_screen import CameraWarningScreen
from ui.map_screen import MapScreen
from admin_ui.admin_login_screen import AdminLoginScreen
from database.schema import create_database_schema
from paths import ensure_directories
from paths import ensure_directories

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

        self.previous_screen_before_map = None

        self.map_screen = MapScreen(
            on_back=self.go_back_from_map
        )
        self.welcome_screen = WelcomeScreen(
            on_start=self.go_to_department_screen
        )

        self.tryon_screen = TryOnScreen(
            on_exit=self.exit_virtual_try_on
        )

        self.admin_login_screen = AdminLoginScreen(
            on_login=self.handle_admin_login,
            on_cancel=self.go_to_department_screen
        )

        self.department_screen = DepartmentScreen(
            on_department_selected=self.go_to_category_screen,
            on_back=self.go_to_welcome_screen,
            on_map=self.go_to_map_screen,
            on_staff_access=self.go_to_admin_login
        )

        self.category_screen = CategoryScreen(
            on_category_selected=self.go_to_catalogue_screen,
            on_back=self.go_to_department_screen,
            on_map=self.go_to_map_screen
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

        self.camera_warning_screen = CameraWarningScreen(
            on_cancel=self.go_back_to_product_detail,
            on_agree=self.start_virtual_try_on
        )

        self.stack.addWidget(self.welcome_screen)
        self.stack.addWidget(self.department_screen)
        self.stack.addWidget(self.category_screen)
        self.stack.addWidget(self.catalogue_screen)
        self.stack.addWidget(self.product_detail_screen)
        self.stack.addWidget(self.camera_warning_screen)
        self.stack.setCurrentWidget(self.welcome_screen)
        self.stack.addWidget(self.map_screen)
        self.stack.addWidget(self.tryon_screen)
        self.stack.addWidget(self.admin_login_screen)

    def go_to_welcome_screen(self):
        self.stack.setCurrentWidget(self.welcome_screen)

    def go_to_admin_login(self):
        self.admin_login_screen.clear_form()
        self.stack.setCurrentWidget(
            self.admin_login_screen
        )
    
    # Testing admin screen
    def handle_admin_login(self, username, password):
        if username == "admin" and password == "admin123":
            self.admin_login_screen.clear_error()
            self.admin_login_screen.show_success("access verified")
            print("Admin login successful")
            print("Next screen will be Admin Dashboard")
        else:
            self.admin_login_screen.show_error(
                "Incorrect username or password."
            )

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
        self.camera_warning_screen.set_product(product)
        self.stack.setCurrentWidget(self.camera_warning_screen)
    
    def go_to_map_screen(self):
        self.previous_screen_before_map = self.stack.currentWidget()
        self.map_screen.set_product(self.selected_product)
        self.stack.setCurrentWidget(self.map_screen)

    def go_back_to_product_detail(self):
        self.stack.setCurrentWidget(self.product_detail_screen)


    def start_virtual_try_on(self, product):
        self.selected_product = product
        self.tryon_screen.start_camera(product)
        self.stack.setCurrentWidget(self.tryon_screen)
    

    def go_back_from_map(self):
        if hasattr(self, "previous_screen_before_map") and self.previous_screen_before_map:
            self.stack.setCurrentWidget(self.previous_screen_before_map)
        else:
            self.stack.setCurrentWidget(self.department_screen)

    def exit_virtual_try_on(self):
        self.tryon_screen.stop_camera()
        self.stack.setCurrentWidget(self.product_detail_screen)

if __name__ == "__main__":
    ensure_directories()
    create_database_schema()
    app = QApplication(sys.argv)

    window = SmartMirrorApp()
    window.show()

    sys.exit(app.exec())