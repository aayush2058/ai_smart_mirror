import cv2
import numpy as np
import json
import os


class ClothingOverlay:

    def __init__(self, catalogue_path="data\catalogue.json"):

        # -------------------------
        # LOAD CATALOGUE FROM JSON
        # -------------------------
        self.catalogue_path = catalogue_path
        self.catalogue = self._load_catalogue()

        self.current_index = 0

        # Create image path list from catalogue
        self.path = [item["image"] for item in self.catalogue]

        # -------------------------
        # GROUP FILTERING
        # -------------------------
        self.selected_group = None
        self.filtered_indexes = []

        # No outfit shown by default
        self.outfit_selected = False
        self.shirt = None

        # -------------------------
        # SMOOTHING VALUES
        # -------------------------
        self.smooth_x = None
        self.smooth_y = None
        self.smooth_width = None
        self.smooth_height = None
        self.smooth_angle = None

        # -------------------------
        # CONFIG FILE
        # -------------------------
        self.config_path = "config.json"

        # Default fit calibration values
        self.width_scale = 1.7
        self.height_scale = 1.3
        self.vertical_offset = 0.12
        self.smoothing_factor = 0.45
        self.arm_occlusion = True

        # Load saved calibration if config.json exists
        self.load_config()

        # -------------------------
        # REALISM SETTINGS
        # -------------------------
        self.arm_occlusion = True

    def _load_catalogue(self):

        if not os.path.exists(self.catalogue_path):
            print("❌ catalogue.json not found:", self.catalogue_path)
            return []

        try:
            with open(self.catalogue_path, "r", encoding="utf-8") as file:
                catalogue = json.load(file)

            if not isinstance(catalogue, list) or len(catalogue) == 0:
                print("❌ Catalogue is empty or invalid.")
                return []

            print("✅ Catalogue loaded:", self.catalogue_path)
            return catalogue

        except Exception as e:
            print("❌ Error loading catalogue:", e)
            return []

    def _get_indexes_for_group(self, group_name):

        indexes = []

        for i, item in enumerate(self.catalogue):

            name = item.get("name", "").lower()
            category = item.get("category", "").lower()

            pants_keywords = ["pant", "pants", "trouser", "trousers", "jeans"]

            is_pants = any(
                word in name or word in category
                for word in pants_keywords
            )

            if group_name == "Shirts":
                # Everything that is not pants is treated as Shirts for now
                if not is_pants:
                    indexes.append(i)

            elif group_name == "Pants":
                if is_pants:
                    indexes.append(i)

        return indexes

    def set_group(self, group_name):

        self.selected_group = group_name
        self.filtered_indexes = self._get_indexes_for_group(group_name)

        if len(self.filtered_indexes) == 0:
            print("❌ No products found for:", group_name)
            self.outfit_selected = False
            self.shirt = None
            self._reset_smoothing()
            return

        self.current_index = self.filtered_indexes[0]

        self.shirt = cv2.imread(
            self.path[self.current_index],
            cv2.IMREAD_UNCHANGED
        )

        if self.shirt is None:
            print("❌ Clothing image not loaded:", self.path[self.current_index])
            self.outfit_selected = False
        else:
            print("✅ Selected group:", group_name)
            print("✅ Clothing image loaded:", self.path[self.current_index])
            self.outfit_selected = True

        self._reset_smoothing()

    def remove_outfit(self):

        self.selected_group = None
        self.filtered_indexes = []
        self.outfit_selected = False
        self.shirt = None
        self._reset_smoothing()

        print("✅ Outfit removed")

    def has_outfit(self):
        return self.outfit_selected and self.shirt is not None

    def get_menu_groups(self):
        return ["Shirts", "Pants", "Remove Outfit"]

    def get_current_product(self):

        if not self.has_outfit():
            return None

        if not self.catalogue:
            return None

        return self.catalogue[self.current_index]

    def next_cloth(self):

        if not self.outfit_selected:
            print("❌ Select an outfit type first.")
            return

        if not self.catalogue or len(self.path) == 0:
            print("❌ No products available in catalogue.")
            return

        if len(self.filtered_indexes) == 0:
            print("❌ No products available in selected group:", self.selected_group)
            return

        current_position = self.filtered_indexes.index(self.current_index)

        next_position = current_position + 1

        if next_position >= len(self.filtered_indexes):
            next_position = 0

        self.current_index = self.filtered_indexes[next_position]

        self.shirt = cv2.imread(
            self.path[self.current_index],
            cv2.IMREAD_UNCHANGED
        )

        if self.shirt is None:
            print("❌ Clothing image not loaded:", self.path[self.current_index])
            self.outfit_selected = False
        else:
            print("✅ Next clothing:", self.path[self.current_index])
            self.outfit_selected = True

        self._reset_smoothing()

    def previous_cloth(self):

        if not self.outfit_selected:
            print("❌ Select an outfit type first.")
            return

        if not self.catalogue or len(self.path) == 0:
            print("❌ No products available in catalogue.")
            return

        if len(self.filtered_indexes) == 0:
            print("❌ No products available in selected group:", self.selected_group)
            return

        current_position = self.filtered_indexes.index(self.current_index)

        previous_position = current_position - 1

        if previous_position < 0:
            previous_position = len(self.filtered_indexes) - 1

        self.current_index = self.filtered_indexes[previous_position]

        self.shirt = cv2.imread(
            self.path[self.current_index],
            cv2.IMREAD_UNCHANGED
        )

        if self.shirt is None:
            print("❌ Clothing image not loaded:", self.path[self.current_index])
            self.outfit_selected = False
        else:
            print("✅ Previous clothing:", self.path[self.current_index])
            self.outfit_selected = True

        self._reset_smoothing()

    def draw_shirt(self, frame, landmarks, mode):

        # No outfit by default
        if not self.has_outfit():
            return frame

        if landmarks is None or self.shirt is None:
            return frame

        original_frame = frame.copy()

        h, w = frame.shape[:2]

        ls = landmarks[11]
        rs = landmarks[12]
        lh = landmarks[23]

        # -------------------------
        # SHOULDER POINTS
        # -------------------------
        lx, ly = int(ls.x * w), int(ls.y * h)
        rx, ry = int(rs.x * w), int(rs.y * h)

        # -------------------------
        # CENTER POINT
        # -------------------------
        cx = (lx + rx) // 2
        cy = (ly + ry) // 2

        # -------------------------
        # ROTATION ANGLE
        # -------------------------
        angle = cv2.fastAtan2(ry - ly, rx - lx)

        if angle > 90:
            angle = angle - 180

        angle = max(-35, min(35, angle))

        angle = self._smooth_value(self.smooth_angle, angle)
        self.smooth_angle = angle

        # -------------------------
        # SIZE CALCULATION
        # -------------------------
        shoulder_width = abs(rx - lx)

        torso_height = int(abs(lh.y - ls.y) * h * self.height_scale)

        if shoulder_width < 10:
            return frame

        width = int(shoulder_width * self.width_scale)

        width = self._smooth_value(self.smooth_width, width)
        torso_height = self._smooth_value(self.smooth_height, torso_height)

        self.smooth_width = width
        self.smooth_height = torso_height

        width = max(width, 1)
        torso_height = max(torso_height, 1)

        if width <= 0 or torso_height <= 0:
            return frame

        clothing = cv2.resize(self.shirt, (width, torso_height))

        # -------------------------
        # MODE ADJUSTMENTS
        # -------------------------
        if mode == "FRONT":
            pass

        elif mode == "BACK":
            clothing = cv2.flip(clothing, 1)

        elif mode == "SIDE":
            width = int(width * 0.85)

            if width <= 0 or torso_height <= 0:
                return frame

            clothing = cv2.resize(clothing, (width, torso_height))

        # -------------------------
        # POSITION
        # -------------------------
        x = cx - width // 2
        y = cy - int(torso_height * self.vertical_offset)

        x = self._smooth_value(self.smooth_x, x)
        y = self._smooth_value(self.smooth_y, y)

        self.smooth_x = x
        self.smooth_y = y

        # -------------------------
        # ROTATION EFFECT
        # -------------------------
        M = cv2.getRotationMatrix2D(
            (width // 2, torso_height // 2),
            angle,
            1
        )

        try:
            clothing = cv2.warpAffine(clothing, M, (width, torso_height))
        except:
            return frame

        frame = self._overlay(frame, clothing, x, y)

        if self.arm_occlusion:
            frame = self._apply_arm_occlusion(
                frame,
                original_frame,
                landmarks,
                shoulder_width
            )

        return frame

    # -------------------------
    # LIVE FIT CALIBRATION METHODS
    # -------------------------
    def increase_width(self):
        self.width_scale += 0.05
        print("Width scale:", round(self.width_scale, 2))
        self._reset_smoothing()

    def decrease_width(self):
        self.width_scale = max(0.8, self.width_scale - 0.05)
        print("Width scale:", round(self.width_scale, 2))
        self._reset_smoothing()

    def increase_height(self):
        self.height_scale += 0.05
        print("Height scale:", round(self.height_scale, 2))
        self._reset_smoothing()

    def decrease_height(self):
        self.height_scale = max(0.6, self.height_scale - 0.05)
        print("Height scale:", round(self.height_scale, 2))
        self._reset_smoothing()

    def move_up(self):
        self.vertical_offset += 0.02
        print("Vertical offset:", round(self.vertical_offset, 2))
        self._reset_smoothing()

    def move_down(self):
        self.vertical_offset = max(0.0, self.vertical_offset - 0.02)
        print("Vertical offset:", round(self.vertical_offset, 2))
        self._reset_smoothing()

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
    
    def load_config(self):
        if not os.path.exists(self.config_path):
            print("ℹ️ No config.json found. Using default calibration.")
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                config = json.load(file)

            self.width_scale = config.get("width_scale", self.width_scale)
            self.height_scale = config.get("height_scale", self.height_scale)
            self.vertical_offset = config.get("vertical_offset", self.vertical_offset)
            self.smoothing_factor = config.get("smoothing_factor", self.smoothing_factor)
            self.arm_occlusion = config.get("arm_occlusion", self.arm_occlusion)

            print("✅ Calibration loaded from config.json")
            print("Width scale:", self.width_scale)
            print("Height scale:", self.height_scale)
            print("Vertical offset:", self.vertical_offset)
            print("Smoothing factor:", self.smoothing_factor)
            print("Arm occlusion:", self.arm_occlusion)

        except Exception as e:
            print("❌ Error loading config.json:", e)


    def save_config(self):
        config = {
            "width_scale": round(self.width_scale, 3),
            "height_scale": round(self.height_scale, 3),
            "vertical_offset": round(self.vertical_offset, 3),
            "smoothing_factor": round(self.smoothing_factor, 3),
            "arm_occlusion": self.arm_occlusion
        }

        try:
            with open(self.config_path, "w", encoding="utf-8") as file:
                json.dump(config, file, indent=4)

            print("✅ Calibration saved to config.json")
            print(config)

        except Exception as e:
            print("❌ Error saving config.json:", e)

    def _reset_smoothing(self):

        self.smooth_x = None
        self.smooth_y = None
        self.smooth_width = None
        self.smooth_height = None
        self.smooth_angle = None

    def _smooth_value(self, old_value, new_value):

        if old_value is None:
            return new_value

        return int(
            old_value * (1 - self.smoothing_factor) +
            new_value * self.smoothing_factor
        )

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