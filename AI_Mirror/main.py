import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from paths import ensure_directories
from database.schema import create_database_schema

from services.product_service import ProductCatalog
from services.auth_service import AuthService

from ui.welcome_screen import WelcomeScreen
from ui.department_screen import DepartmentScreen
from ui.category_screen import CategoryScreen
from ui.catalogue_screen import CatalogueScreen
from ui.product_detail_screen import ProductDetailScreen
from ui.camera_warning_screen import CameraWarningScreen
from ui.map_screen import MapScreen
from ui.tryon_screen import TryOnScreen
from admin_ui.product_form_screen import ProductFormScreen
from services.product_service import ProductService
from services.image_service import ImageService
from admin_ui.product_management_screen import ProductManagementScreen

from admin_ui.admin_login_screen import AdminLoginScreen
from admin_ui.admin_dashboard_screen import AdminDashboardScreen


class SmartMirrorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Smart Mirror")
        self.setMinimumSize(1200, 800)

        self.selected_department = None
        self.selected_category = None
        self.selected_product = None
        self.previous_screen_before_map = None

        self.current_admin = None
        self.auth_service = AuthService()
        self.product_service = ProductService()
        self.image_service = ImageService()
        self.catalog = ProductCatalog()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.welcome_screen = WelcomeScreen(
            on_start=self.go_to_department_screen
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

        self.product_form_screen = ProductFormScreen(
            on_save=self.save_new_product,
            on_cancel=self.go_to_manage_products,
            on_upload_image=self.upload_product_image
        )

        self.product_detail_screen = ProductDetailScreen(
            on_back=self.go_back_to_catalogue,
            on_try_on=self.go_to_camera_warning_screen,
            on_map=self.go_to_map_screen
        )

        self.product_management_screen = ProductManagementScreen(
            on_back=self.go_to_admin_dashboard,
            on_add_product=self.go_to_add_product,
            on_edit_product=self.go_to_edit_product,
            on_delete_product=self.delete_product_from_admin
        )
        
        self.camera_warning_screen = CameraWarningScreen(
            on_cancel=self.go_back_to_product_detail,
            on_agree=self.start_virtual_try_on
        )

        self.map_screen = MapScreen(
            on_back=self.go_back_from_map
        )

        self.tryon_screen = TryOnScreen(
            on_exit=self.exit_virtual_try_on
        )

        self.admin_login_screen = AdminLoginScreen(
            on_login=self.handle_admin_login,
            on_cancel=self.go_to_department_screen
        )

        self.admin_dashboard_screen = AdminDashboardScreen(
            on_products=self.go_to_manage_products,
            on_add_product=self.go_to_add_product,
            on_inventory=self.go_to_inventory,
            on_discounts=self.go_to_discounts,
            on_locations=self.go_to_locations,
            on_tryon_settings=self.go_to_tryon_settings,
            on_logout=self.logout_admin
        )

        self.stack.addWidget(self.welcome_screen)
        self.stack.addWidget(self.department_screen)
        self.stack.addWidget(self.category_screen)
        self.stack.addWidget(self.catalogue_screen)
        self.stack.addWidget(self.product_detail_screen)
        self.stack.addWidget(self.camera_warning_screen)
        self.stack.addWidget(self.map_screen)
        self.stack.addWidget(self.tryon_screen)
        self.stack.addWidget(self.admin_login_screen)
        self.stack.addWidget(self.admin_dashboard_screen)
        self.stack.addWidget(self.product_management_screen)
        self.stack.setCurrentWidget(self.welcome_screen)
        self.stack.addWidget(self.product_form_screen)

    def go_to_welcome_screen(self):
        self.stack.setCurrentWidget(self.welcome_screen)

    def go_to_department_screen(self):
        self.stack.setCurrentWidget(self.department_screen)

    def go_to_admin_login(self):
        self.admin_login_screen.clear_form()
        self.stack.setCurrentWidget(self.admin_login_screen)

    def handle_admin_login(self, username, password):
        print("Login received in main.py:", username)

        admin = self.auth_service.authenticate(username, password)

        if admin:
            self.current_admin = admin
            self.admin_login_screen.show_success("Access verified")
            self.update_admin_dashboard_summary()
            self.stack.setCurrentWidget(self.admin_dashboard_screen)
        else:
            self.admin_login_screen.show_error("Incorrect username or password.")

    def update_admin_dashboard_summary(self):
        products = self.catalog.products

        total = len(products)

        available = sum(
            1 for product in products
            if product.get("available", False)
        )

        discounted = sum(
            1 for product in products
            if product.get("discount", False)
        )

        tryon_enabled = sum(
            1 for product in products
            if product.get("tryon_category")
        )

        self.admin_dashboard_screen.update_summary(
            total,
            available,
            discounted,
            tryon_enabled
        )

    def go_to_manage_products(self):
        self.catalog.reload()
        self.product_management_screen.set_products(self.catalog.products)
        self.stack.setCurrentWidget(self.product_management_screen)

    def go_to_add_product(self):
        self.product_form_screen.clear_form()
        self.stack.setCurrentWidget(self.product_form_screen)

    def go_to_inventory(self):
        print("Stock & Sizes clicked")

    def go_to_discounts(self):
        print("Discounts clicked")

    def go_to_locations(self):
        print("Store Locations clicked")

    def go_to_tryon_settings(self):
        print("Try-On Settings clicked")

    def logout_admin(self):
        self.current_admin = None
        self.admin_login_screen.clear_form()
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

    def go_back_to_product_detail(self):
        self.stack.setCurrentWidget(self.product_detail_screen)

    def upload_product_image(self, file_path, tryon_category):
        return self.image_service.save_product_image(
            file_path,
            tryon_category
        )

    def save_new_product(self, product_data):
        product_id = self.product_service.add_product(product_data)

        print("Product saved with ID:", product_id)

        self.product_form_screen.clear_form()
        self.go_to_manage_products()

    def start_virtual_try_on(self, product):
        self.selected_product = product
        self.tryon_screen.start_camera(product)
        self.stack.setCurrentWidget(self.tryon_screen)

    def exit_virtual_try_on(self):
        self.tryon_screen.stop_camera()
        self.stack.setCurrentWidget(self.product_detail_screen)

    def go_to_admin_dashboard(self):
        self.update_admin_dashboard_summary()
        self.stack.setCurrentWidget(self.admin_dashboard_screen)


    def go_to_edit_product(self, product):
        print("Edit product:", product.get("name"))


    def delete_product_from_admin(self, product):
        print("Delete product:", product.get("name"))

    def go_to_map_screen(self):
        self.previous_screen_before_map = self.stack.currentWidget()
        self.map_screen.set_product(self.selected_product)
        self.stack.setCurrentWidget(self.map_screen)

    def go_back_from_map(self):
        if self.previous_screen_before_map:
            self.stack.setCurrentWidget(self.previous_screen_before_map)
        else:
            self.stack.setCurrentWidget(self.department_screen)




if __name__ == "__main__":
    ensure_directories()
    create_database_schema()

    app = QApplication(sys.argv)

    window = SmartMirrorApp()
    window.show()

    sys.exit(app.exec())