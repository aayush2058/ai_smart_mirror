import cv2
import numpy as np


class ClothingOverlay:

    def __init__(self, path=None):

        # -------------------------
        # CLOTHING IMAGE LIST
        # -------------------------
        if path is None:
            path = [
                "img/shirt1.png",
                "img/shirt2.png",
                "img/shirt3.png",
                "img/shirt4.png",
                "img/shirt5.png",
            ]

        self.path = path
        self.current_index = 0

        self.shirt = cv2.imread(self.path[self.current_index], cv2.IMREAD_UNCHANGED)

        if self.shirt is None:
            print("❌ Shirt image not loaded:", self.path[self.current_index])
        else:
            print("✅ Shirt image loaded:", self.path[self.current_index])

        # -------------------------
        # SMOOTHING VALUES
        # -------------------------
        self.smooth_x = None
        self.smooth_y = None
        self.smooth_width = None
        self.smooth_height = None
        self.smooth_angle = None

        # Lower value = smoother but slower response
        # Higher value = faster response but more shaky
        self.smoothing_factor = 0.45

        # -------------------------
        # REALISM SETTINGS
        # -------------------------
        self.arm_occlusion = True

    def draw_shirt(self, frame, landmarks, mode):

        if landmarks is None or self.shirt is None:
            return frame

        # Save original frame before shirt is drawn
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

        # Prevent sudden upside-down rotation
        if angle > 90:
            angle = angle - 180

        # Limit rotation to natural body tilt
        angle = max(-35, min(35, angle))

        # Smooth rotation angle
        angle = self._smooth_value(self.smooth_angle, angle)
        self.smooth_angle = angle

        # -------------------------
        # SIZE CALCULATION
        # -------------------------
        shoulder_width = abs(rx - lx)
        height_scale = 1.3
        torso_height = int(abs(lh.y - ls.y) * h * height_scale)

        if shoulder_width < 10:
            return frame

        width_scale = 1.7
        width = int(shoulder_width * width_scale)

        # Smooth shirt width and height
        width = self._smooth_value(self.smooth_width, width)
        torso_height = self._smooth_value(self.smooth_height, torso_height)

        self.smooth_width = width
        self.smooth_height = torso_height

        width = max(width, 1)
        torso_height = max(torso_height, 1)

        if width <= 0 or torso_height <= 0:
            return frame

        shirt = cv2.resize(self.shirt, (width, torso_height))

        # -------------------------
        # MODE ADJUSTMENTS
        # -------------------------
        if mode == "FRONT":
            pass

        elif mode == "BACK":
            shirt = cv2.flip(shirt, 1)

        elif mode == "SIDE":
            width = int(width * 0.85)

            if width <= 0 or torso_height <= 0:
                return frame

            shirt = cv2.resize(shirt, (width, torso_height))

        # -------------------------
        # POSITION
        # -------------------------
        x = cx - width // 2

        vertical_offset = 0.12
        y = cy - int(torso_height * vertical_offset)

        # Smooth shirt position
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
            shirt = cv2.warpAffine(shirt, M, (width, torso_height))
        except:
            return frame

        # Draw shirt first
        frame = self._overlay(frame, shirt, x, y)

        # Then put arms back on top of shirt
        if self.arm_occlusion:
            frame = self._apply_arm_occlusion(
                frame,
                original_frame,
                landmarks,
                shoulder_width
            )

        return frame

    def next_cloth(self):

        self.current_index += 1

        if self.current_index >= len(self.path):
            self.current_index = 0

        self.shirt = cv2.imread(self.path[self.current_index], cv2.IMREAD_UNCHANGED)

        if self.shirt is None:
            print("❌ Shirt image not loaded:", self.path[self.current_index])
        else:
            print("✅ Shirt image loaded:", self.path[self.current_index])

        self._reset_smoothing()

    def previous_cloth(self):

        self.current_index -= 1

        if self.current_index < 0:
            self.current_index = len(self.path) - 1

        self.shirt = cv2.imread(self.path[self.current_index], cv2.IMREAD_UNCHANGED)

        if self.shirt is None:
            print("❌ Shirt image not loaded:", self.path[self.current_index])
        else:
            print("✅ Shirt image loaded:", self.path[self.current_index])

        self._reset_smoothing()

    def _apply_arm_occlusion(self, frame, original_frame, landmarks, shoulder_width):

        H, W = frame.shape[:2]

        # Empty black mask
        arm_mask = np.zeros((H, W), dtype=np.uint8)

        # Arm landmark groups:
        # Left arm: shoulder 11, elbow 13, wrist 15
        # Right arm: shoulder 12, elbow 14, wrist 16
        arms = [
            [11, 13, 15],
            [12, 14, 16]
        ]

        # Arm thickness based on body size
        thickness = int(max(12, shoulder_width * 0.16))

        for arm in arms:

            points = []

            for idx in arm:
                lm = landmarks[idx]
                x = int(lm.x * W)
                y = int(lm.y * H)
                points.append((x, y))

            shoulder, elbow, wrist = points

            # Draw upper arm and lower arm on mask
            cv2.line(arm_mask, shoulder, elbow, 255, thickness)
            cv2.line(arm_mask, elbow, wrist, 255, thickness)

            # Add circles at joints to avoid gaps
            cv2.circle(arm_mask, shoulder, thickness // 2, 255, -1)
            cv2.circle(arm_mask, elbow, thickness // 2, 255, -1)
            cv2.circle(arm_mask, wrist, thickness // 2, 255, -1)

        # Smooth mask edges
        arm_mask = cv2.GaussianBlur(arm_mask, (15, 15), 0)

        # Convert mask to 0–1 alpha
        alpha = arm_mask.astype(float) / 255.0
        alpha = alpha[:, :, None]

        # Put original arm pixels back on top of shirt
        frame = (
            alpha * original_frame +
            (1 - alpha) * frame
        ).astype("uint8")

        return frame

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