import cv2
import numpy as np
import json
import os
from pathlib import Path
from fit_engine import FitEngine
from services.tryon_catalogue_service import TryOnCatalogueService


class ClothingOverlay:

    def __init__(self, catalogue_path="data/catalogue.json"):

        self.engine_root = Path(__file__).resolve().parent
        self.project_root = self.engine_root.parent
        self.catalogue_path = str(self.project_root / catalogue_path)
        self.catalogue_service = TryOnCatalogueService(
            fallback_path=self.catalogue_path
        )

        self.catalogue = self._load_catalogue()
        self.path = [item.get("image", "") for item in self.catalogue]
        

        # Outfit state
        self.active_group = None

        self.shirt_index = None
        self.pants_index = None

        self.shirt_image = None
        self.pants_image = None

        # Shirt parts
        self.shirt_body_image = None
        self.left_sleeve_image = None
        self.right_sleeve_image = None

        self.shirt_indexes = self._get_indexes_for_group("Shirts")
        self.pants_indexes = self._get_indexes_for_group("Pants")

        # Shirt smoothing
        self.shirt_smooth_x = None
        self.shirt_smooth_y = None
        self.shirt_smooth_width = None
        self.shirt_smooth_height = None
        self.shirt_smooth_angle = None

        # Sleeve movement removed. Full shirt image is used for upper-body rendering.
        self.edit_mode = "BODY"

        # Pants smoothing
        self.pants_smooth_x = None
        self.pants_smooth_y = None
        self.pants_smooth_width = None
        self.pants_smooth_height = None

        # Config path
        self.config_path = str(self.engine_root / "config.json")
        
        # Default shirt fitting
        self.shirt_width_scale = 1.7
        self.shirt_height_scale = 1.3
        self.shirt_vertical_offset = 0.12
        self.shirt_horizontal_offset = 0

        # Default pants fitting
        self.pants_width_scale = 1.35
        self.pants_height_scale = 1.15
        self.pants_vertical_offset = 0.02
        self.pants_horizontal_offset = 0

        # General settings
        self.smoothing_factor = 0.45
        self.arm_occlusion = False
        self.leg_occlusion = False

        # Smart fitting engine - used for shirt first
        self.fit_engine = FitEngine(smoothing=0.35)

        self.load_config()

    # ============================================================
    # LOAD CATALOGUE
    # ============================================================
    def _load_catalogue(self):
        catalogue = self.catalogue_service.load_products()

        if not catalogue:
            print("No valid try-on products were found.")
            return []

        print("Try-on catalogue source:", self.catalogue_service.source)
        return catalogue

    # ============================================================
    # CONFIG LOAD / SAVE
    # ============================================================
    def load_config(self):

        if not os.path.exists(self.config_path):
            print("ℹ️ No config.json found. Using default calibration.")
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                config = json.load(file)

            self.shirt_width_scale = config.get("shirt_width_scale", self.shirt_width_scale)
            self.shirt_height_scale = config.get("shirt_height_scale", self.shirt_height_scale)
            self.shirt_vertical_offset = config.get("shirt_vertical_offset", self.shirt_vertical_offset)
            self.shirt_horizontal_offset = config.get("shirt_horizontal_offset", self.shirt_horizontal_offset)

            self.pants_width_scale = config.get("pants_width_scale", self.pants_width_scale)
            self.pants_height_scale = config.get("pants_height_scale", self.pants_height_scale)
            self.pants_vertical_offset = config.get("pants_vertical_offset", self.pants_vertical_offset)
            self.pants_horizontal_offset = config.get("pants_horizontal_offset", self.pants_horizontal_offset)

            self.smoothing_factor = config.get("smoothing_factor", self.smoothing_factor)
            self.arm_occlusion = config.get("arm_occlusion", self.arm_occlusion)
            self.leg_occlusion = config.get("leg_occlusion", self.leg_occlusion)

            print("✅ Calibration loaded from config.json")

        except Exception as e:
            print("❌ Error loading config.json:", e)

    def save_config(self):

        config = {
            "shirt_width_scale": round(self.shirt_width_scale, 3),
            "shirt_height_scale": round(self.shirt_height_scale, 3),
            "shirt_vertical_offset": round(self.shirt_vertical_offset, 3),
            "shirt_horizontal_offset": int(self.shirt_horizontal_offset),

            "pants_width_scale": round(self.pants_width_scale, 3),
            "pants_height_scale": round(self.pants_height_scale, 3),
            "pants_vertical_offset": round(self.pants_vertical_offset, 3),
            "pants_horizontal_offset": int(self.pants_horizontal_offset),

            "smoothing_factor": round(self.smoothing_factor, 3),
            "arm_occlusion": self.arm_occlusion,
            "leg_occlusion": self.leg_occlusion
        }

        try:
            with open(self.config_path, "w", encoding="utf-8") as file:
                json.dump(config, file, indent=4)

            print("✅ Calibration saved to config.json")
            print(config)

        except Exception as e:
            print("❌ Error saving config.json:", e)

    # ============================================================
    # PRODUCT-SPECIFIC FIT SAVE
    # ============================================================
    def save_current_product_fit(self):

        if self.active_group is None:
            print("❌ Select Shirts or Pants first.")
            return

        if self.active_group == "Shirts":

            if self.shirt_index is None:
                print("❌ No shirt selected.")
                return

            product_index = self.shirt_index

            fit_data = {
                "width_scale": round(self.shirt_width_scale, 3),
                "height_scale": round(self.shirt_height_scale, 3),
                "vertical_offset": round(self.shirt_vertical_offset, 3),
                "horizontal_offset": int(self.shirt_horizontal_offset)
            }

        elif self.active_group == "Pants":

            if self.pants_index is None:
                print("❌ No pants selected.")
                return

            product_index = self.pants_index

            fit_data = {
                "width_scale": round(self.pants_width_scale, 3),
                "height_scale": round(self.pants_height_scale, 3),
                "vertical_offset": round(self.pants_vertical_offset, 3),
                "horizontal_offset": int(self.pants_horizontal_offset)
            }

        else:
            print("❌ Invalid active group.")
            return

        self.catalogue[product_index]["fit"] = fit_data

        product = self.catalogue[product_index]

        if self.catalogue_service.update_fit(product, fit_data):
            print("Product-specific fit saved to SQLite.")
            print("Product:", product.get("name"))
            print("Fit:", fit_data)
        else:
            print("Product fit could not be saved to SQLite.")

    # ============================================================
    # GROUP / IMAGE HELPERS
    # ============================================================
    def _get_indexes_for_group(self, group_name):

        indexes = []

        for i, item in enumerate(self.catalogue):

            tryon_category = item.get("tryon_category", "")
            category = item.get("category", "")

            final_category = tryon_category if tryon_category else category
            final_category = final_category.strip().lower()

            if group_name.strip().lower() == final_category:
                indexes.append(i)

        return indexes

    def _load_image_by_index(self, index):

        if index is None:
            return None

        if index < 0 or index >= len(self.catalogue):
            return None

        image_path = self.catalogue[index].get("image", "")
        full_image_path = self.project_root / image_path

        print("Trying to load:", full_image_path)

        if not full_image_path.exists():
            print("❌ File does not exist:", full_image_path)
            return None

        image = cv2.imread(str(full_image_path), cv2.IMREAD_UNCHANGED)

        if image is None:
            print("❌ Clothing image not loaded:", full_image_path)
            return None

        print("✅ Clothing image loaded:", full_image_path)
        return image
    
    def _load_image_from_path(self, relative_path):

        if not relative_path:
            return None

        full_path = self.project_root / relative_path

        if not full_path.exists():
            print("❌ Part image not found:", full_path)
            return None

        image = cv2.imread(str(full_path), cv2.IMREAD_UNCHANGED)

        if image is None:
            print("❌ Part image failed to load:", full_path)
            return None

        print("✅ Part image loaded:", full_path)
        return image
    
    def _load_shirt_parts(self, product_index):
        """
        Sleeve movement has been removed.

        This function is intentionally kept as a no-op so existing calls do
        not break. The system now always uses the normal full shirt image from
        the catalogue "image" field.
        """
        self.shirt_body_image = None
        self.left_sleeve_image = None
        self.right_sleeve_image = None
        return

    def _apply_product_fit_to_controls(self, product_index, group_name):

        if product_index is None:
            return

        if product_index < 0 or product_index >= len(self.catalogue):
            return

        product = self.catalogue[product_index]
        fit = product.get("fit", {})

        if group_name == "Shirts":

            self.shirt_width_scale = fit.get("width_scale", self.shirt_width_scale)
            self.shirt_height_scale = fit.get("height_scale", self.shirt_height_scale)
            self.shirt_vertical_offset = fit.get("vertical_offset", self.shirt_vertical_offset)
            self.shirt_horizontal_offset = fit.get("horizontal_offset", self.shirt_horizontal_offset)
            

            print("✅ Shirt fit applied:", product.get("name"))
            print(fit)

        elif group_name == "Pants":

            self.pants_width_scale = fit.get("width_scale", self.pants_width_scale)
            self.pants_height_scale = fit.get("height_scale", self.pants_height_scale)
            self.pants_vertical_offset = fit.get("vertical_offset", self.pants_vertical_offset)
            self.pants_horizontal_offset = fit.get("horizontal_offset", self.pants_horizontal_offset)

            print("✅ Pants fit applied:", product.get("name"))
            print(fit)

    # ============================================================
    # MENU ACTIONS
    # ============================================================
    def set_group(self, group_name):

        if group_name == "Shirts":
            self.select_shirt()
            return

        if group_name == "Pants":
            self.select_pants()
            return

        if group_name == "Remove Shirt":
            self.remove_shirt()
            return

        if group_name == "Remove Pants":
            self.remove_pants()
            return

        if group_name == "Remove All":
            self.remove_all()
            return
        
    def select_product_from_interface(self, selected_product):
        """
        Selects one product passed from the PySide6 catalogue interface.
        This avoids using the old gesture menu for first product selection.
        """

        if selected_product is None:
            print("❌ No selected product received from interface.")
            return

        selected_id = selected_product.get("id")
        selected_name = selected_product.get("name")
        selected_image = selected_product.get("image")

        product_index = None

        for i, item in enumerate(self.catalogue):
            same_id = selected_id is not None and item.get("id") == selected_id
            same_name = selected_name is not None and item.get("name") == selected_name
            same_image = selected_image is not None and item.get("image") == selected_image

            if same_id or same_name or same_image:
                product_index = i
                break

        if product_index is None:
            print("❌ Product not found in try-on catalogue:", selected_name)
            return

        product = self.catalogue[product_index]

        # Admin previews carry unsaved slider values in `fit`. Apply them to
        # this in-memory catalogue instance without writing catalogue.json.
        preview_fit = selected_product.get("fit")
        if preview_fit:
            product["fit"] = dict(preview_fit)

        tryon_category = product.get("tryon_category", "")
        category = product.get("category", "")

        if tryon_category:
            product_type = tryon_category
        elif category == "Upper Fit":
            product_type = "Shirts"
        elif category == "Lower Fit":
            product_type = "Pants"
        else:
            product_type = category

        if product_type == "Shirts":
            self.active_group = "Shirts"
            self.shirt_index = product_index
            self.shirt_image = self._load_image_by_index(product_index)
            self._apply_product_fit_to_controls(product_index, "Shirts")
            self._reset_shirt_smoothing()
            print("✅ Interface selected shirt:", product.get("name"))

        elif product_type == "Pants":
            self.active_group = "Pants"
            self.pants_index = product_index
            self.pants_image = self._load_image_by_index(product_index)
            self._apply_product_fit_to_controls(product_index, "Pants")
            self._reset_pants_smoothing()
            print("✅ Interface selected pants:", product.get("name"))

        else:
            print("❌ Unsupported try-on category:", product_type)

    def select_shirt(self):

        self.active_group = "Shirts"

        if len(self.shirt_indexes) == 0:
            print("❌ No shirt products found.")
            return

        if self.shirt_index is None:
            self.shirt_index = self.shirt_indexes[0]

        self.shirt_image = self._load_image_by_index(self.shirt_index)
        self._load_shirt_parts(self.shirt_index)
        self._apply_product_fit_to_controls(self.shirt_index, "Shirts")
        self._reset_shirt_smoothing()

        print("✅ Active group: Shirts")

    def select_pants(self):

        self.active_group = "Pants"

        if len(self.pants_indexes) == 0:
            print("❌ No pants products found.")
            return

        if self.pants_index is None:
            self.pants_index = self.pants_indexes[0]

        self.pants_image = self._load_image_by_index(self.pants_index)
        self._apply_product_fit_to_controls(self.pants_index, "Pants")
        self._reset_pants_smoothing()

        print("✅ Active group: Pants")


    def remove_shirt(self):

        self.shirt_index = None
        self.shirt_image = None
        self._reset_shirt_smoothing()

        if self.active_group == "Shirts":
            self.active_group = None

        print("✅ Shirt removed")

    def remove_pants(self):

        self.pants_index = None
        self.pants_image = None
        self._reset_pants_smoothing()

        if self.active_group == "Pants":
            self.active_group = None

        print("✅ Pants removed")

    def remove_all(self):

        self.shirt_index = None
        self.pants_index = None

        self.shirt_image = None
        self.pants_image = None

        self.active_group = None

        self._reset_shirt_smoothing()
        self._reset_pants_smoothing()

        print("✅ All outfits removed")

    def remove_outfit(self):
        self.remove_all()

    def has_outfit(self):
        return self.shirt_image is not None or self.pants_image is not None

    def has_shirt(self):
        return self.shirt_image is not None

    def has_pants(self):
        return self.pants_image is not None

    def get_menu_groups(self):
        return ["Shirts", "Pants", "Remove Shirt", "Remove Pants", "Remove All"]

    # ============================================================
    # PRODUCT INFO
    # ============================================================
    def get_selected_products(self):

        shirt_product = None
        pants_product = None

        if self.shirt_index is not None and self.shirt_image is not None:
            shirt_product = self.catalogue[self.shirt_index]

        if self.pants_index is not None and self.pants_image is not None:
            pants_product = self.catalogue[self.pants_index]

        return {
            "shirt": shirt_product,
            "pants": pants_product,
            "active_group": self.active_group
        }

    def get_current_product(self):

        if self.active_group == "Shirts" and self.shirt_index is not None:
            return self.catalogue[self.shirt_index]

        if self.active_group == "Pants" and self.pants_index is not None:
            return self.catalogue[self.pants_index]

        if self.shirt_index is not None:
            return self.catalogue[self.shirt_index]

        if self.pants_index is not None:
            return self.catalogue[self.pants_index]

        return None

    # ============================================================
    # NEXT / PREVIOUS
    # ============================================================
    def next_cloth(self):

        if self.active_group == "Shirts":
            self.next_shirt()
            return

        if self.active_group == "Pants":
            self.next_pants()
            return

        print("❌ Select Shirts or Pants first.")

    def previous_cloth(self):

        if self.active_group == "Shirts":
            self.previous_shirt()
            return

        if self.active_group == "Pants":
            self.previous_pants()
            return

        print("❌ Select Shirts or Pants first.")

    def next_shirt(self):

        if len(self.shirt_indexes) == 0:
            print("❌ No shirts available.")
            return

        self.active_group = "Shirts"

        if self.shirt_index is None:
            self.shirt_index = self.shirt_indexes[0]
        else:
            current_position = self.shirt_indexes.index(self.shirt_index)
            next_position = current_position + 1

            if next_position >= len(self.shirt_indexes):
                next_position = 0

            self.shirt_index = self.shirt_indexes[next_position]

        self.shirt_image = self._load_image_by_index(self.shirt_index)
        self._load_shirt_parts(self.shirt_index)
        self._apply_product_fit_to_controls(self.shirt_index, "Shirts")
        self._reset_shirt_smoothing()

    def previous_shirt(self):

        if len(self.shirt_indexes) == 0:
            print("❌ No shirts available.")
            return

        self.active_group = "Shirts"

        if self.shirt_index is None:
            self.shirt_index = self.shirt_indexes[0]
        else:
            current_position = self.shirt_indexes.index(self.shirt_index)
            previous_position = current_position - 1

            if previous_position < 0:
                previous_position = len(self.shirt_indexes) - 1

            self.shirt_index = self.shirt_indexes[previous_position]

        self.shirt_image = self._load_image_by_index(self.shirt_index)
        self._apply_product_fit_to_controls(self.shirt_index, "Shirts")
        self._reset_shirt_smoothing()

    def next_pants(self):

        if len(self.pants_indexes) == 0:
            print("❌ No pants available.")
            return

        self.active_group = "Pants"

        if self.pants_index is None:
            self.pants_index = self.pants_indexes[0]
        else:
            current_position = self.pants_indexes.index(self.pants_index)
            next_position = current_position + 1

            if next_position >= len(self.pants_indexes):
                next_position = 0

            self.pants_index = self.pants_indexes[next_position]

        self.pants_image = self._load_image_by_index(self.pants_index)
        self._load_shirt_parts(self.shirt_index)
        self._apply_product_fit_to_controls(self.pants_index, "Pants")
        self._reset_pants_smoothing()

    def previous_pants(self):

        if len(self.pants_indexes) == 0:
            print("❌ No pants available.")
            return

        self.active_group = "Pants"

        if self.pants_index is None:
            self.pants_index = self.pants_indexes[0]
        else:
            current_position = self.pants_indexes.index(self.pants_index)
            previous_position = current_position - 1

            if previous_position < 0:
                previous_position = len(self.pants_indexes) - 1

            self.pants_index = self.pants_indexes[previous_position]

        self.pants_image = self._load_image_by_index(self.pants_index)
        self._apply_product_fit_to_controls(self.pants_index, "Pants")
        self._reset_pants_smoothing()

    # ============================================================
    # MAIN DRAW METHOD
    # ============================================================
    def draw_outfits(self, frame, landmarks, mode):

        if landmarks is None:
            return frame

        # Pants first, shirt second
        if self.pants_image is not None:
            frame = self._draw_pants(frame, landmarks, mode)

        if self.shirt_image is not None:
            frame = self._draw_upper_body(frame, landmarks, mode)

        return frame

    def draw_shirt(self, frame, landmarks, mode):
        return self.draw_outfits(frame, landmarks, mode)

    # ============================================================
    # DRAW SHIRT
    # ============================================================
    def _draw_upper_body(self, frame, landmarks, mode):

        original_frame = frame.copy()

        body = self.fit_engine.measure(landmarks, frame.shape)

        left_shoulder = body["left_shoulder"]
        right_shoulder = body["right_shoulder"]

        lx, ly = left_shoulder
        rx, ry = right_shoulder

        angle = cv2.fastAtan2(ry - ly, rx - lx)

        if angle > 90:
            angle = angle - 180

        angle = max(-35, min(35, angle))

        angle = self._smooth_value(self.shirt_smooth_angle, angle)
        self.shirt_smooth_angle = angle

        shoulder_width = body["shoulder_width"]

        if shoulder_width < 10:
            return frame

        x, y, width, torso_height = self.fit_engine.shirt_box(
            body,
            self.shirt_width_scale,
            self.shirt_height_scale,
            self.shirt_vertical_offset,
            self.shirt_horizontal_offset
        )

        width = self._smooth_value(self.shirt_smooth_width, width)
        torso_height = self._smooth_value(self.shirt_smooth_height, torso_height)

        self.shirt_smooth_width = width
        self.shirt_smooth_height = torso_height

        width = max(width, 1)
        torso_height = max(torso_height, 1)

        x = self._smooth_value(self.shirt_smooth_x, x)
        y = self._smooth_value(self.shirt_smooth_y, y)

        self.shirt_smooth_x = x
        self.shirt_smooth_y = y

        # Sleeve movement removed.
        # Always draw the full shirt image from catalogue["image"].
        clothing = cv2.resize(
            self.shirt_image,
            (width, torso_height)
        )

        if mode == "BACK":
            clothing = cv2.flip(clothing, 1)

        elif mode == "SIDE":
            width = int(width * 0.85)
            width = max(width, 1)
            clothing = cv2.resize(clothing, (width, torso_height))

        M = cv2.getRotationMatrix2D(
            (width // 2, torso_height // 2),
            angle,
            1
        )

        try:
            clothing = cv2.warpAffine(
                clothing,
                M,
                (width, torso_height),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(0, 0, 0, 0)
            )
        except Exception:
            return frame

        frame = self._overlay(frame, clothing, x, y)

        frame = self._add_soft_body_shadow(
            frame,
            x,
            y,
            width,
            torso_height,
            strength=0.03
        )

        if self.arm_occlusion:
            frame = self._apply_arm_occlusion(
                frame,
                original_frame,
                landmarks,
                shoulder_width
            )

        return frame

    # ============================================================
    # DRAW PANTS
    # ============================================================
    def _draw_pants(self, frame, landmarks, mode):

        original_frame = frame.copy()

        h, w = frame.shape[:2]

        body = self.fit_engine.measure(landmarks, frame.shape)

        hip_center_x, hip_center_y = body["hip_center"]
        hip_width = body["hip_width"]
        leg_height = body["leg_height"]

        pants_height = int(leg_height * self.pants_height_scale)

        if hip_width < 10 or pants_height < 10:
            return frame

        width = int(hip_width * self.pants_width_scale)

        width = self._smooth_value(self.pants_smooth_width, width)
        pants_height = self._smooth_value(self.pants_smooth_height, pants_height)

        self.pants_smooth_width = width
        self.pants_smooth_height = pants_height

        width = max(width, 1)
        pants_height = max(pants_height, 1)

        pants = cv2.resize(self.pants_image, (width, pants_height))

        if mode == "BACK":
            pants = cv2.flip(pants, 1)

        elif mode == "SIDE":
            width = int(width * 0.75)
            pants = cv2.resize(pants, (width, pants_height))

        x = hip_center_x - width // 2 + self.pants_horizontal_offset
        y = hip_center_y - int(pants_height * self.pants_vertical_offset)

        x = self._smooth_value(self.pants_smooth_x, x)
        y = self._smooth_value(self.pants_smooth_y, y)

        self.pants_smooth_x = x
        self.pants_smooth_y = y

        frame = self._overlay(frame, pants, x, y)

        frame = self._restore_inside_leg_gap(
            frame,
            original_frame,
            landmarks
        )

        if self.leg_occlusion:
            frame = self._apply_leg_occlusion(
                frame,
                original_frame,
                landmarks,
                hip_width
            )

        return frame

    # ============================================================
    # LIVE FIT CALIBRATION
    # ============================================================
    def increase_width(self):

        if self.active_group == "Pants":
            self.pants_width_scale += 0.05
            print("Pants width scale:", round(self.pants_width_scale, 2))
            self._reset_pants_smoothing()
        else:
            self.shirt_width_scale += 0.05
            print("Shirt width scale:", round(self.shirt_width_scale, 2))
            self._reset_shirt_smoothing()

    def decrease_width(self):

        if self.active_group == "Pants":
            self.pants_width_scale = max(0.5, self.pants_width_scale - 0.05)
            print("Pants width scale:", round(self.pants_width_scale, 2))
            self._reset_pants_smoothing()
        else:
            self.shirt_width_scale = max(0.8, self.shirt_width_scale - 0.05)
            print("Shirt width scale:", round(self.shirt_width_scale, 2))
            self._reset_shirt_smoothing()

    def increase_height(self):

        if self.active_group == "Pants":
            self.pants_height_scale += 0.05
            print("Pants height scale:", round(self.pants_height_scale, 2))
            self._reset_pants_smoothing()
        else:
            self.shirt_height_scale += 0.05
            print("Shirt height scale:", round(self.shirt_height_scale, 2))
            self._reset_shirt_smoothing()

    def decrease_height(self):

        if self.active_group == "Pants":
            self.pants_height_scale = max(0.5, self.pants_height_scale - 0.05)
            print("Pants height scale:", round(self.pants_height_scale, 2))
            self._reset_pants_smoothing()
        else:
            self.shirt_height_scale = max(0.6, self.shirt_height_scale - 0.05)
            print("Shirt height scale:", round(self.shirt_height_scale, 2))
            self._reset_shirt_smoothing()

    def move_up(self):

        if self.active_group == "Pants":
            self.pants_vertical_offset += 0.02
            print("Pants vertical offset:", round(self.pants_vertical_offset, 2))
            self._reset_pants_smoothing()
        else:
            self.shirt_vertical_offset += 0.02
            print("Shirt vertical offset:", round(self.shirt_vertical_offset, 2))
            self._reset_shirt_smoothing()

    def move_down(self):

        if self.active_group == "Pants":
            self.pants_vertical_offset = max(0.0, self.pants_vertical_offset - 0.02)
            print("Pants vertical offset:", round(self.pants_vertical_offset, 2))
            self._reset_pants_smoothing()
        else:
            self.shirt_vertical_offset = max(0.0, self.shirt_vertical_offset - 0.02)
            print("Shirt vertical offset:", round(self.shirt_vertical_offset, 2))
            self._reset_shirt_smoothing()

    def move_left(self):

        if self.active_group == "Pants":
            self.pants_horizontal_offset -= 5
            print("Pants horizontal offset:", self.pants_horizontal_offset)
            self._reset_pants_smoothing()
        else:
            self.shirt_horizontal_offset -= 5
            print("Shirt horizontal offset:", self.shirt_horizontal_offset)
            self._reset_shirt_smoothing()

    def move_right(self):

        if self.active_group == "Pants":
            self.pants_horizontal_offset += 5
            print("Pants horizontal offset:", self.pants_horizontal_offset)
            self._reset_pants_smoothing()
        else:
            self.shirt_horizontal_offset += 5
            print("Shirt horizontal offset:", self.shirt_horizontal_offset)
            self._reset_shirt_smoothing()

    # ============================================================
    # OCCLUSION / BODY WRAP
    # ============================================================
    def _apply_arm_occlusion(self, frame, original_frame, landmarks, shoulder_width):

        H, W = frame.shape[:2]

        arm_mask = np.zeros((H, W), dtype=np.uint8)

        arms = [
            [11, 13, 15],
            [12, 14, 16]
        ]

        thickness = int(max(12, shoulder_width * 0.16))

        for arm in arms:

            points = []

            for idx in arm:
                lm = landmarks[idx]
                x = int(lm.x * W)
                y = int(lm.y * H)
                points.append((x, y))

            shoulder, elbow, wrist = points

            cv2.line(arm_mask, shoulder, elbow, 255, thickness)
            cv2.line(arm_mask, elbow, wrist, 255, thickness)

            cv2.circle(arm_mask, shoulder, thickness // 2, 255, -1)
            cv2.circle(arm_mask, elbow, thickness // 2, 255, -1)
            cv2.circle(arm_mask, wrist, thickness // 2, 255, -1)

        arm_mask = cv2.GaussianBlur(arm_mask, (15, 15), 0)

        alpha = arm_mask.astype(float) / 255.0
        alpha = alpha[:, :, None]

        frame = (
            alpha * original_frame +
            (1 - alpha) * frame
        ).astype("uint8")

        return frame

    def _apply_leg_occlusion(self, frame, original_frame, landmarks, hip_width):

        H, W = frame.shape[:2]

        leg_mask = np.zeros((H, W), dtype=np.uint8)

        legs = [
            [23, 25, 27],
            [24, 26, 28]
        ]

        thickness = int(max(8, hip_width * 0.08))

        for leg in legs:

            points = []

            for idx in leg:
                lm = landmarks[idx]
                x = int(lm.x * W)
                y = int(lm.y * H)
                points.append((x, y))

            hip, knee, ankle = points

            cv2.line(leg_mask, hip, knee, 255, thickness)
            cv2.line(leg_mask, knee, ankle, 255, thickness)

            cv2.circle(leg_mask, hip, thickness // 2, 255, -1)
            cv2.circle(leg_mask, knee, thickness // 2, 255, -1)
            cv2.circle(leg_mask, ankle, thickness // 2, 255, -1)

        leg_mask = cv2.GaussianBlur(leg_mask, (15, 15), 0)

        alpha = leg_mask.astype(float) / 255.0
        alpha = alpha[:, :, None]

        frame = (
            alpha * original_frame +
            (1 - alpha) * frame
        ).astype("uint8")

        return frame

    def _apply_upper_body_clip(self, original_frame, outfit_frame, landmarks):

        H, W = original_frame.shape[:2]

        ls = landmarks[11]
        rs = landmarks[12]
        lh = landmarks[23]
        rh = landmarks[24]

        left_shoulder = (int(ls.x * W), int(ls.y * H))
        right_shoulder = (int(rs.x * W), int(rs.y * H))
        left_hip = (int(lh.x * W), int(lh.y * H))
        right_hip = (int(rh.x * W), int(rh.y * H))

        shoulder_width = abs(right_shoulder[0] - left_shoulder[0])
        hip_width = abs(right_hip[0] - left_hip[0])

        shoulder_expand = int(shoulder_width * 0.25)
        waist_expand = int(max(8, hip_width * 0.12))

        body_poly = np.array([
            (left_shoulder[0] - shoulder_expand, left_shoulder[1]),
            (right_shoulder[0] + shoulder_expand, right_shoulder[1]),
            (right_hip[0] + waist_expand, right_hip[1]),
            (left_hip[0] - waist_expand, left_hip[1])
        ], dtype=np.int32)

        mask = np.zeros((H, W), dtype=np.uint8)
        cv2.fillPoly(mask, [body_poly], 255)
        mask = cv2.GaussianBlur(mask, (21, 21), 0)

        alpha = mask.astype(float) / 255.0
        alpha = alpha[:, :, None]

        result = (
            alpha * outfit_frame +
            (1 - alpha) * original_frame
        ).astype("uint8")

        return result

    def _apply_lower_body_clip(self, original_frame, outfit_frame, landmarks):

        H, W = original_frame.shape[:2]

        lh = landmarks[23]
        rh = landmarks[24]
        lk = landmarks[25]
        rk = landmarks[26]
        la = landmarks[27]
        ra = landmarks[28]

        left_hip = (int(lh.x * W), int(lh.y * H))
        right_hip = (int(rh.x * W), int(rh.y * H))
        left_knee = (int(lk.x * W), int(lk.y * H))
        right_knee = (int(rk.x * W), int(rk.y * H))
        left_ankle = (int(la.x * W), int(la.y * H))
        right_ankle = (int(ra.x * W), int(ra.y * H))

        hip_width = abs(right_hip[0] - left_hip[0])
        expand = int(max(10, hip_width * 0.18))

        crotch_x = (left_hip[0] + right_hip[0]) // 2
        crotch_y = int(
            (left_hip[1] + right_hip[1]) / 2 +
            abs(left_knee[1] - left_hip[1]) * 0.35
        )
        crotch = (crotch_x, crotch_y)

        mask = np.zeros((H, W), dtype=np.uint8)

        left_leg_poly = np.array([
            (left_hip[0] - expand, left_hip[1]),
            crotch,
            (left_knee[0] + expand // 2, left_knee[1]),
            (left_ankle[0] + expand // 2, left_ankle[1]),
            (left_ankle[0] - expand // 2, left_ankle[1]),
            (left_knee[0] - expand, left_knee[1])
        ], dtype=np.int32)

        right_leg_poly = np.array([
            crotch,
            (right_hip[0] + expand, right_hip[1]),
            (right_knee[0] + expand, right_knee[1]),
            (right_ankle[0] + expand // 2, right_ankle[1]),
            (right_ankle[0] - expand // 2, right_ankle[1]),
            (right_knee[0] - expand // 2, right_knee[1])
        ], dtype=np.int32)

        cv2.fillPoly(mask, [left_leg_poly], 255)
        cv2.fillPoly(mask, [right_leg_poly], 255)
        mask = cv2.GaussianBlur(mask, (21, 21), 0)

        alpha = mask.astype(float) / 255.0
        alpha = alpha[:, :, None]

        result = (
            alpha * outfit_frame +
            (1 - alpha) * original_frame
        ).astype("uint8")

        return result

    def _restore_inside_leg_gap(self, frame, original_frame, landmarks):

        H, W = frame.shape[:2]

        lh = landmarks[23]
        rh = landmarks[24]
        lk = landmarks[25]
        rk = landmarks[26]

        left_hip = (int(lh.x * W), int(lh.y * H))
        right_hip = (int(rh.x * W), int(rh.y * H))
        left_knee = (int(lk.x * W), int(lk.y * H))
        right_knee = (int(rk.x * W), int(rk.y * H))

        hip_width = abs(right_hip[0] - left_hip[0])

        crotch_x = (left_hip[0] + right_hip[0]) // 2
        crotch_y = int(
            (left_hip[1] + right_hip[1]) / 2 +
            abs(left_knee[1] - left_hip[1]) * 0.30
        )

        gap_bottom_x = (left_knee[0] + right_knee[0]) // 2
        gap_bottom_y = (left_knee[1] + right_knee[1]) // 2

        gap_width = int(max(4, hip_width * 0.10))

        gap_poly = np.array([
            (crotch_x, crotch_y),
            (gap_bottom_x - gap_width, gap_bottom_y),
            (gap_bottom_x + gap_width, gap_bottom_y)
        ], dtype=np.int32)

        mask = np.zeros((H, W), dtype=np.uint8)
        cv2.fillPoly(mask, [gap_poly], 255)
        mask = cv2.GaussianBlur(mask, (11, 11), 0)

        alpha = mask.astype(float) / 255.0
        alpha = alpha[:, :, None]

        result = (
            alpha * original_frame +
            (1 - alpha) * frame
        ).astype("uint8")

        return result

    # ============================================================
    # HELPERS
    # ============================================================
    def _reset_shirt_smoothing(self):

        self.shirt_smooth_x = None
        self.shirt_smooth_y = None
        self.shirt_smooth_width = None
        self.shirt_smooth_height = None
        self.shirt_smooth_angle = None

    def _reset_pants_smoothing(self):

        self.pants_smooth_x = None
        self.pants_smooth_y = None
        self.pants_smooth_width = None
        self.pants_smooth_height = None

    def _smooth_value(self, old_value, new_value):

        if old_value is None:
            return new_value

        return int(
            old_value * (1 - self.smoothing_factor) +
            new_value * self.smoothing_factor
        )
    
    def _add_soft_body_shadow(self, frame, x, y, width, height, strength=0.05):

        H, W = frame.shape[:2]

        x1 = max(0, int(x))
        y1 = max(0, int(y))
        x2 = min(W, int(x + width))
        y2 = min(H, int(y + height))

        if x1 >= x2 or y1 >= y2:
            return frame

        roi = frame[y1:y2, x1:x2]

        h, w = roi.shape[:2]

        if w <= 1 or h <= 1:
            return frame

        gradient = np.linspace(-1, 1, w).reshape(1, w, 1)
        side_shadow = np.abs(gradient)

        shadow = 1 - (side_shadow * strength)

        roi = (roi.astype(float) * shadow).clip(0, 255).astype("uint8")

        frame[y1:y2, x1:x2] = roi

        return frame

    def _overlay(self, frame, img, x, y):

        h, w = img.shape[:2]
        H, W = frame.shape[:2]

        if x >= W or y >= H:
            return frame

        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(W, x + w)
        y2 = min(H, y + h)

        ix1 = max(0, -x)
        iy1 = max(0, -y)
        ix2 = ix1 + (x2 - x1)
        iy2 = iy1 + (y2 - y1)

        if x1 >= x2 or y1 >= y2:
            return frame

        if img.shape[2] == 4:

            alpha = img[iy1:iy2, ix1:ix2, 3] / 255.0
            alpha = alpha[:, :, None]

            frame[y1:y2, x1:x2] = (
                alpha * img[iy1:iy2, ix1:ix2, :3] +
                (1 - alpha) * frame[y1:y2, x1:x2]
            ).astype("uint8")

        else:
            frame[y1:y2, x1:x2] = img[iy1:iy2, ix1:ix2]

        return frame
    
    def _angle_between_points(self, p1, p2):

        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]

        angle = np.degrees(np.arctan2(dy, dx))
        return angle
    
    def _rotate_image(self, image, angle):

        if image is None:
            return None

        h, w = image.shape[:2]
        center = (w // 2, h // 2)

        M = cv2.getRotationMatrix2D(center, angle, 1.0)

        rotated = cv2.warpAffine(
            image,
            M,
            (w, h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0, 0)
        )

        return rotated
    
