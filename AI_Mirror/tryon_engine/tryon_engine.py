import sys
from pathlib import Path

import cv2


ENGINE_ROOT = Path(__file__).resolve().parent

if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))


class TryOnEngine:
    def __init__(self):
        self.started = False
        self.selected_product = None

        self.body = None
        self.clothes = None
        self.segmenter = None

        self.camera_module = None

        self.view_mode = "FRONT"
        self.use_segmentation = False
        self.debug = False

    def start(self, selected_product):
        """
        Starts camera and loads selected product.
        This should only be called after camera consent.
        """

        if self.started:
            return True

        self.selected_product = selected_product

        from camera import start_camera, get_frame, release, get_status
        from bodytracking import BodyTracker
        from clothing_overlay import ClothingOverlay
        from segmentation import PersonSegmenter

        self.camera_module = {
            "start_camera": start_camera,
            "get_frame": get_frame,
            "release": release,
            "get_status": get_status,
        }

        self.body = BodyTracker()
        self.clothes = ClothingOverlay(catalogue_path="data/catalogue.json")
        self.segmenter = PersonSegmenter()

        if not self.camera_module["start_camera"]():
            self.stop()
            return False

        if selected_product is not None:
            self.clothes.select_product_from_interface(selected_product)

        self.started = True
        return True

    def read_frame(self):
        """
        Returns one processed BGR frame for PySide6.
        No cv2.imshow() here.
        """

        if not self.started or self.camera_module is None:
            return None

        frame, landmarks = self.camera_module["get_frame"]()

        if frame is None:
            return None

        if landmarks is not None:
            self.view_mode = self.body.get_body_orientation(landmarks)

            # Keep front-only for now because your current testing was front-focused.
            self.view_mode = "FRONT"

            original_frame = frame.copy()

            frame = self.clothes.draw_outfits(
                frame,
                landmarks,
                self.view_mode
            )

            if self.use_segmentation and self.clothes.has_outfit():
                frame = self.segmenter.keep_overlay_inside_person(
                    original_frame,
                    frame
                )

            if self.debug:
                frame = self.body.draw_landmarks(frame, landmarks)

        return frame

    def camera_status(self):
        if self.camera_module is None:
            return {"state": "idle"}
        return self.camera_module["get_status"]()

    def stop(self):
        """
        Stops camera safely.
        """

        if self.camera_module is not None:
            self.camera_module["release"]()

        self.started = False
        self.selected_product = None
        self.body = None
        self.clothes = None
        self.segmenter = None
        self.camera_module = None
