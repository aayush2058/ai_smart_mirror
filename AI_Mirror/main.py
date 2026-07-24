import sys


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(errors="replace")

from admin_ui.tryon.tryon_settings_screen import TryOnSettingsScreen
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from admin_ui.discounts.discount_management_screen import DiscountManagementScreen
from paths import ensure_directories
from database.schema import create_database_schema
from services.inventory_service import InventoryService
from services.product_service import ProductCatalog
from services.auth_service import AuthService
from admin_ui.inventory.inventory_management_screen import InventoryManagementScreen
from ui.welcome_screen import WelcomeScreen
from ui.department_screen import DepartmentScreen
from ui.category_screen import CategoryScreen
from ui.catalogue_screen import CatalogueScreen
from ui.product_detail_screen import ProductDetailScreen
from ui.camera_warning_screen import CameraWarningScreen
from ui.map_screen import MapScreen
from ui.tryon_screen import TryOnScreen
from admin_ui.products.product_form_screen import ProductFormScreen
from services.product_service import ProductService
from services.image_service import ImageService
from services.admin_undo_service import AdminUndoService
from admin_ui.history.change_history_screen import ChangeHistoryScreen
from services.health_service import HealthService
from services.logging_service import configure_logging
from services.runtime_heartbeat import RuntimeHeartbeat
from services.basket_service import BasketService
from ui.basket_screen import BasketScreen
from admin_ui.analytics.event_tracker import EventTracker
from admin_ui.analytics.metrics_service import MetricsService
from admin_ui.analytics.analytics_dashboard_screen import AnalyticsDashboardScreen
from admin_ui.diagnostics.system_diagnostics_screen import SystemDiagnosticsScreen
from admin_ui.products.product_management_screen import ProductManagementScreen
from PySide6.QtWidgets import QMessageBox
from admin_ui.auth.admin_login_screen import AdminLoginScreen
from admin_ui.dashboard.admin_dashboard_screen import AdminDashboardScreen
from admin_ui.locations.location_management_screen import LocationManagementScreen
from admin_ui.products.deleted_products_screen import DeletedProductsScreen
from services.prediction_service import PredictionService
from admin_ui.superadmin.super_admin_dashboard import SuperAdminDashboard
from admin_ui.superadmin.account_management_screen import AccountManagementScreen
from admin_ui.superadmin.prediction_dashboard_screen import PredictionDashboardScreen
from admin_ui.widgets.control_styles import application_control_styles

class SmartMirrorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Smart Mirror")
        self.setMinimumSize(1200, 800)
        self.tryon_opened_from_admin = False
        self.selected_department = None
        self.selected_category = None
        self.selected_product = None
        self.previous_screen_before_map = None
        self.inventory_service = InventoryService()
        self.current_admin = None
        self.auth_service = AuthService()
        self.product_service = ProductService()
        self.image_service = ImageService()
        self.admin_undo_service = AdminUndoService()
        self.health_service = HealthService()
        self.logger = configure_logging()
        self.runtime_heartbeat = RuntimeHeartbeat(self)
        self.basket_service = BasketService()
        self.event_tracker = EventTracker()
        self.metrics_service = MetricsService()
        self.prediction_service = PredictionService()
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

        self.inventory_management_screen = InventoryManagementScreen(
            on_back=self.go_to_admin_dashboard,
            on_update_stock=self.go_to_update_stock
        )

        self.product_detail_screen = ProductDetailScreen(
            on_back=self.go_back_to_catalogue,
            on_try_on=self.go_to_camera_warning_screen,
            on_map=self.go_to_map_screen,
            on_add_to_basket=self.add_product_to_basket,
            on_view_basket=self.go_to_basket,
        )

        self.basket_screen = BasketScreen(
            basket_service=self.basket_service,
            on_back=self.go_back_from_basket,
            on_clear=self.basket_cleared,
        )

        self.product_management_screen = ProductManagementScreen(
            on_back=self.go_to_admin_dashboard,
            on_add_product=self.go_to_add_product,
            on_edit_product=self.go_to_edit_product,
            on_delete_product=self.delete_product_from_admin,
            on_deleted_products=self.go_to_deleted_products
        )
        
        self.camera_warning_screen = CameraWarningScreen(
            on_cancel=self.go_back_to_product_detail,
            on_agree=self.start_virtual_try_on
        )

        self.map_screen = MapScreen(
            on_back=self.go_back_from_map
        )

        self.discount_management_screen = DiscountManagementScreen(
            on_back=self.go_to_admin_dashboard,
            on_update_discount=self.update_product_discount
        )

        self.location_management_screen = LocationManagementScreen(
            on_back=self.go_to_admin_dashboard,
            on_update_location=self.update_product_location
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
            on_diagnostics=self.go_to_system_diagnostics,
            on_analytics=self.go_to_retail_insights,
            on_undo=self.undo_last_admin_change,
            on_history=self.go_to_change_history,
            on_logout=self.logout_admin,
            on_super_back=self.go_to_super_admin_dashboard,
        )


        self.tryon_settings_screen = TryOnSettingsScreen(
            on_back=self.go_to_admin_dashboard,
            on_update_tryon=self.update_product_tryon_settings,
            on_preview_tryon=self.preview_admin_tryon_fit,
            on_toggle_tryon=self.toggle_product_tryon,
        )

        self.system_diagnostics_screen = SystemDiagnosticsScreen(
            health_service=self.health_service,
            camera_status=self.tryon_screen.engine.camera_status,
            on_reset_camera=self.reset_camera_from_diagnostics,
            on_back=self.go_to_admin_dashboard,
        )

        self.analytics_dashboard_screen = AnalyticsDashboardScreen(
            metrics_service=self.metrics_service,
            on_back=self.go_to_admin_dashboard,
        )

        self.change_history_screen = ChangeHistoryScreen(
            history_service=self.admin_undo_service,
            on_back=self.go_to_admin_dashboard,
            on_changed=self.update_admin_dashboard_summary,
        )

        self.super_admin_dashboard = SuperAdminDashboard(
            on_admin=self.go_to_regular_admin_controls,
            on_predictions=self.go_to_prediction_dashboard,
            on_accounts=self.go_to_account_management,
            on_insights=self.go_to_retail_insights,
            on_diagnostics=self.go_to_system_diagnostics,
            on_history=self.go_to_change_history,
            on_logout=self.logout_admin,
        )

        self.account_management_screen = AccountManagementScreen(
            auth_service=self.auth_service,
            current_user=lambda: self.current_admin,
            on_back=self.go_to_super_admin_dashboard,
        )

        self.prediction_dashboard_screen = PredictionDashboardScreen(
            prediction_service=self.prediction_service,
            current_user=lambda: self.current_admin,
            on_back=self.go_to_super_admin_dashboard,
        )

        self.deleted_products_screen = DeletedProductsScreen(
            on_back=self.go_to_manage_products,
            on_restore_product=self.restore_deleted_product
        )

        self.stack.addWidget(self.tryon_settings_screen)
        self.stack.addWidget(self.welcome_screen)
        self.stack.addWidget(self.department_screen)
        self.stack.addWidget(self.category_screen)
        self.stack.addWidget(self.catalogue_screen)
        self.stack.addWidget(self.product_detail_screen)
        self.stack.addWidget(self.basket_screen)
        self.stack.addWidget(self.camera_warning_screen)
        self.stack.addWidget(self.map_screen)
        self.stack.addWidget(self.tryon_screen)
        self.stack.addWidget(self.admin_login_screen)
        self.stack.addWidget(self.admin_dashboard_screen)
        self.stack.addWidget(self.product_management_screen)
        self.stack.setCurrentWidget(self.welcome_screen)
        self.stack.addWidget(self.product_form_screen)
        self.stack.addWidget(self.inventory_management_screen)
        self.stack.addWidget(self.location_management_screen)
        self.stack.addWidget(self.discount_management_screen)
        self.stack.addWidget(self.deleted_products_screen)
        self.stack.addWidget(self.system_diagnostics_screen)
        self.stack.addWidget(self.analytics_dashboard_screen)
        self.stack.addWidget(self.change_history_screen)
        self.stack.addWidget(self.super_admin_dashboard)
        self.stack.addWidget(self.account_management_screen)
        self.stack.addWidget(self.prediction_dashboard_screen)

        self.logger.info("Smart Mirror application initialized")
        self.runtime_heartbeat.start()
        self.event_tracker.track("session_started")

    def closeEvent(self, event):
        self.runtime_heartbeat.stop()
        self.tryon_screen.stop_camera()
        self.logger.info("Smart Mirror application closed")
        super().closeEvent(event)

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
            if admin.get("role") == "super_admin":
                self.go_to_super_admin_dashboard()
            else:
                self.admin_dashboard_screen.set_super_mode(False)
                self.stack.setCurrentWidget(self.admin_dashboard_screen)
        else:
            self.admin_login_screen.show_error("Incorrect username or password.")

    def update_admin_dashboard_summary(self):
        products = self.product_service.get_products()
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
        low_stock = sum(1 for product in products if 0 < int(product.get("stock_quantity", 0)) <= 3)
        out_of_stock = sum(1 for product in products if not product.get("available", False))

        self.admin_dashboard_screen.update_summary(
            total,
            available,
            discounted,
            tryon_enabled,
            low_stock,
            out_of_stock,
        )

    def go_to_manage_products(self):
        products = self.product_service.get_products()
        self.product_management_screen.set_products(products)
        self.stack.setCurrentWidget(self.product_management_screen)
        
    def go_to_add_product(self):
        self.product_form_screen.set_add_mode()
        self.stack.setCurrentWidget(self.product_form_screen)

    def go_to_inventory(self):
        products = []

        for product in self.product_service.get_products():
            full_product = self.product_service.get_product(product.get("id"))
            if full_product:
                products.append(full_product)

        self.inventory_management_screen.set_products(products)
        self.stack.setCurrentWidget(self.inventory_management_screen)

    def go_to_update_stock(self, product, sizes):
        product_id = product.get("id")

        if not product_id:
            print("Product ID missing. Cannot update stock.")
            return

        self.admin_undo_service.apply_inventory_change(
            product_id, product.get("name", "Product"), sizes
        )

        print("Stock updated:", product.get("name"))

        self.go_to_inventory()

    def preview_admin_tryon_fit(self, product):
        self.tryon_opened_from_admin = True
        self.selected_product = product

        self.tryon_screen.start_camera(product)

        self.stack.setCurrentWidget(
            self.tryon_screen
        )

    def go_to_discounts(self):
        products = self.product_service.get_products()
        self.discount_management_screen.set_products(products)
        self.stack.setCurrentWidget(self.discount_management_screen)

    def go_to_locations(self):
        products = self.product_service.get_products()
        self.location_management_screen.set_products(products)
        self.stack.setCurrentWidget(self.location_management_screen)
    
    def update_product_location(self, product, location):
        product_id = product.get("id")

        if not product_id:
            print("Product ID missing. Cannot update location.")
            return

        success = self.admin_undo_service.apply_product_change(
            product_id, product.get("name", "Product"), "Location",
            {"location": location}, "Updated store location"
        )

        if success:
            print("Location updated:", product.get("name"))
            self.go_to_locations()
        else:
            print("Location update failed:", product.get("name"))
    
    def update_product_discount(self, product, discount_enabled, discount_type, discount_value, discount_price):
        product_id = product.get("id")

        if not product_id:
            print("Product ID missing. Cannot update discount.")
            return

        success = self.admin_undo_service.apply_product_change(
            product_id, product.get("name", "Product"), "Discount",
            {
                "discount": int(discount_enabled),
                "discount_price": discount_price,
                "discount_type": discount_type,
                "discount_value": discount_value,
            }, "Updated product discount"
        )

        if success:
            print("Discount updated:", product.get("name"))
            self.go_to_discounts()
            self.update_admin_dashboard_summary()
        else:
            print("Discount update failed:", product.get("name"))

    def go_to_tryon_settings(self):
        products = []

        for product in self.product_service.get_products():
            full_product = self.product_service.get_product(product.get("id"))
            if full_product:
                products.append(full_product)

        self.tryon_settings_screen.set_products(products)
        self.stack.setCurrentWidget(self.tryon_settings_screen)

    def go_to_system_diagnostics(self):
        self.stack.setCurrentWidget(self.system_diagnostics_screen)

    def go_to_retail_insights(self):
        self.analytics_dashboard_screen.refresh()
        self.stack.setCurrentWidget(self.analytics_dashboard_screen)

    def go_to_change_history(self):
        self.change_history_screen.refresh()
        self.stack.setCurrentWidget(self.change_history_screen)

    def go_to_super_admin_dashboard(self):
        if not self.current_admin or self.current_admin.get("role") != "super_admin":
            self.stack.setCurrentWidget(self.admin_dashboard_screen)
            return
        users = self.auth_service.list_users()
        latest = self.prediction_service.latest()
        self.super_admin_dashboard.set_summary(
            len(users), sum(1 for user in users if user["active"]),
            len(self.product_service.get_products()),
            latest.get("generated_at") if latest else None,
        )
        self.stack.setCurrentWidget(self.super_admin_dashboard)

    def go_to_regular_admin_controls(self):
        self.update_admin_dashboard_summary()
        self.admin_dashboard_screen.set_super_mode(True)
        self.stack.setCurrentWidget(self.admin_dashboard_screen)

    def go_to_account_management(self):
        if not self.current_admin or self.current_admin.get("role") != "super_admin":
            QMessageBox.warning(self, "Access Denied", "Super-admin access is required.")
            return
        self.account_management_screen.refresh()
        self.stack.setCurrentWidget(self.account_management_screen)

    def go_to_prediction_dashboard(self):
        if not self.current_admin or self.current_admin.get("role") != "super_admin":
            QMessageBox.warning(self, "Access Denied", "Super-admin access is required.")
            return
        self.prediction_dashboard_screen.refresh()
        self.stack.setCurrentWidget(self.prediction_dashboard_screen)

    def reset_camera_from_diagnostics(self):
        self.tryon_screen.stop_camera()
        self.logger.info("Camera reset requested from System Diagnostics")
        QMessageBox.information(
            self,
            "Camera Reset",
            "The camera was released safely. It will start fresh at the next virtual try-on.",
        )

    def update_product_tryon_settings(self, product, settings):
        product_id = product.get("id")

        if not product_id:
            print("Product ID missing. Cannot update try-on settings.")
            return

        success = self.admin_undo_service.apply_tryon_settings_change(
            product_id, product.get("name", "Product"), settings
        )

        if success:
            print("Try-on settings updated:", product.get("name"))
            self.go_to_tryon_settings()
        else:
            print("Try-on settings update failed:", product.get("name"))

    def toggle_product_tryon(self, product, enabled):
        product_id = product.get("id")
        if not product_id:
            QMessageBox.warning(self, "Try-On Settings", "Product ID is missing.")
            return

        action = "enable" if enabled else "disable"
        success = self.admin_undo_service.apply_product_change(
            product_id, product.get("name", "Product"), "Try-On Availability",
            {"tryon_enabled": int(enabled)}, f"Changed virtual try-on to {action}d"
        )
        if not success:
            QMessageBox.warning(self, "Try-On Settings", "The setting could not be changed.")
            return

        self.go_to_tryon_settings()
        self.update_admin_dashboard_summary()

    def logout_admin(self):
        self.current_admin = None
        self.admin_login_screen.clear_form()
        self.stack.setCurrentWidget(self.department_screen)

    def undo_last_admin_change(self):
        confirm = QMessageBox.question(
            self,
            "Undo Last Data Change",
            "Restore the product values from before the last recorded correction?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        description = self.admin_undo_service.undo_last_change()
        if description:
            QMessageBox.information(self, "Change Undone", description)
            self.update_admin_dashboard_summary()
        else:
            QMessageBox.information(
                self,
                "Nothing to Undo",
                "No recorded data change is available.",
            )

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
        self.event_tracker.track("product_viewed", product.get("id"))
        self.product_detail_screen.set_product(product)
        self.stack.setCurrentWidget(self.product_detail_screen)

    def go_back_to_catalogue(self):
        self.stack.setCurrentWidget(self.catalogue_screen)

    def add_product_to_basket(self, product, size, quantity=1):
        self.basket_service.add(product, size, quantity)
        self.event_tracker.track("basket_added", product.get("id"), {"size": size, "quantity": quantity})
        self.logger.info("Basket item added: product_id=%s size=%s quantity=%s", product.get("id"), size, quantity)
        QMessageBox.information(
            self,
            "Added to Basket",
            f"{quantity} × {product.get('name', 'Product')} in size {size} added.",
        )

    def go_to_basket(self):
        self.basket_screen.refresh()
        self.event_tracker.track("basket_viewed")
        self.stack.setCurrentWidget(self.basket_screen)

    def go_back_from_basket(self):
        self.stack.setCurrentWidget(self.product_detail_screen)

    def basket_cleared(self):
        self.logger.info("Basket cleared")
        self.event_tracker.track("basket_cleared")

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
        duplicate = next((item for item in self.product_service.get_products()
                          if str(item.get("product_code", "")).lower() == str(product_data.get("product_code", "")).lower()
                          and item.get("id") != self.product_form_screen.editing_product_id), None)
        if duplicate:
            QMessageBox.warning(self, "Duplicate Product Code",
                                f'Product code {product_data.get("product_code")} is already used by {duplicate.get("name")}.' )
            return
        if self.product_form_screen.editing_product_id:
            product_id = self.product_form_screen.editing_product_id

            existing = self.product_service.get_product(product_id) or {}
            product_name = existing.get("name", "Product")
            section_fields = {
                "Price": ("price",),
                "Identity & Category": ("product_code", "name", "department", "category", "colour"),
                "Description": ("description",),
                "Product Image": ("image_path",),
                "Availability": ("available",),
                "Location": ("location",),
                "Discount": ("discount", "discount_price", "discount_type", "discount_value"),
                "Try-On Product Setup": ("tryon_enabled", "tryon_category"),
            }
            results = []
            for section, fields in section_fields.items():
                changes = {
                    field: product_data[field] for field in fields
                    if field in product_data and product_data[field] != existing.get(field)
                }
                if changes:
                    results.append(self.admin_undo_service.apply_product_change(
                        product_id, product_name, section, changes, f"Updated {section.lower()}"
                    ))
            if "sizes" in product_data:
                old_sizes = [{"size": item.get("size"), "quantity": item.get("quantity", 0)}
                             for item in existing.get("sizes", [])]
                if product_data["sizes"] != old_sizes:
                    results.append(self.admin_undo_service.apply_inventory_change(
                        product_id, product_name, product_data["sizes"]
                    ))
            fit_fields = ("width_scale", "height_scale", "vertical_offset", "horizontal_offset")
            new_fit = {field: product_data[field] for field in fit_fields if field in product_data}
            old_fit = existing.get("tryon_settings") or {}
            if new_fit and any(new_fit[field] != old_fit.get(field) for field in new_fit):
                results.append(self.admin_undo_service.apply_tryon_settings_change(
                    product_id, product_name, new_fit
                ))
            success = all(results) if results else True

            if success:
                print("Product updated:", product_id)
            else:
                print("Product update failed:", product_id)

        else:
            self.admin_undo_service.ensure_hourly_backup()
            product_id = self.product_service.add_product(product_data)
            self.admin_undo_service.record_created_product_history(
                product_id, product_data.get("name", "Product")
            )
            print("Product saved with ID:", product_id)

        self.product_form_screen.clear_form()
        self.go_to_manage_products()

        print("Product saved with ID:", product_id)

        self.product_form_screen.clear_form()
        self.go_to_manage_products()

    def start_virtual_try_on(self, product):
        product_id = product.get("id")

        if product_id:
            full_product = self.product_service.get_product_for_tryon(product_id)

            if full_product:
                product = self.prepare_product_for_tryon(full_product)

        self.selected_product = product
        self.event_tracker.track("tryon_started", product.get("id"))
        self.tryon_screen.start_camera(product)
        self.stack.setCurrentWidget(self.tryon_screen)

    def exit_virtual_try_on(self):
        self.tryon_screen.stop_camera()

        if self.tryon_opened_from_admin:
            self.tryon_opened_from_admin = False
            self.go_to_tryon_settings()
            return

        self.stack.setCurrentWidget(
            self.product_detail_screen
        )
        
    def go_to_admin_dashboard(self):
        self.update_admin_dashboard_summary()
        if self.current_admin and self.current_admin.get("role") == "super_admin":
            self.go_to_super_admin_dashboard()
        else:
            self.stack.setCurrentWidget(self.admin_dashboard_screen)


    def go_to_edit_product(self, product):
        product_id = product.get("id")

        if not product_id:
            print("Product ID missing. Cannot edit.")
            return

        full_product = self.product_service.get_product(product_id)

        if not full_product:
            print("Product not found.")
            return

        self.product_form_screen.set_edit_mode(full_product)
        self.stack.setCurrentWidget(self.product_form_screen)


    def delete_product_from_admin(self, product):
        from PySide6.QtWidgets import QMessageBox

        products = product if isinstance(product, list) else [product]

        if not products:
            return

        product_names = "\n".join(
            f"- {item.get('name', 'Unnamed Product')}"
            for item in products
        )

        confirm = QMessageBox.question(
            self,
            "Delete Product",
            f"Are you sure you want to delete:\n\n{product_names}\n\n"
            "These products will be removed from the active catalogue.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        for item in products:
            product_id = item.get("id")

            if product_id:
                self.admin_undo_service.apply_product_change(
                    product_id, item.get("name", "Product"), "Product Status",
                    {"active": 0}, "Deleted product from active catalogue"
                )

        self.go_to_manage_products()
        self.update_admin_dashboard_summary()

    def go_to_map_screen(self):
        self.previous_screen_before_map = self.stack.currentWidget()
        self.map_screen.set_product(self.selected_product)
        self.stack.setCurrentWidget(self.map_screen)

    def go_back_from_map(self):
        if self.previous_screen_before_map:
            self.stack.setCurrentWidget(self.previous_screen_before_map)
        else:
            self.stack.setCurrentWidget(self.department_screen)

    def go_to_deleted_products(self):
        products = self.product_service.get_deleted_products()
        self.deleted_products_screen.set_products(products)
        self.stack.setCurrentWidget(self.deleted_products_screen)


    def restore_deleted_product(self, product):
        product_id = product.get("id")

        if not product_id:
            print("Product ID missing. Cannot restore.")
            return

        success = self.admin_undo_service.apply_product_change(
            product_id, product.get("name", "Product"), "Product Status",
            {"active": 1}, "Restored product to active catalogue"
        )

        if success:
            print("Restored product:", product.get("name"))
            self.go_to_deleted_products()
            self.update_admin_dashboard_summary()
        else:
            print("Restore failed:", product.get("name"))    

    def prepare_product_for_tryon(self, product):
        tryon_settings = product.get("tryon_settings") or {}

        product["fit"] = {
            "width_scale": tryon_settings.get(
                "width_scale",
                product.get("width_scale", 1.0)
            ),
            "height_scale": tryon_settings.get(
                "height_scale",
                product.get("height_scale", 1.0)
            ),
            "vertical_offset": tryon_settings.get(
                "vertical_offset",
                product.get("vertical_offset", 0.0)
            ),
            "horizontal_offset": tryon_settings.get(
                "horizontal_offset",
                product.get("horizontal_offset", 0)
            ),
        }

        product["image"] = (
            product.get("image_path")
            or product.get("image")
            or ""
        )

        return product


if __name__ == "__main__":
    ensure_directories()
    create_database_schema()

    app = QApplication(sys.argv)
    app.setStyleSheet(application_control_styles())

    window = SmartMirrorApp()
    window.show()

    sys.exit(app.exec())
