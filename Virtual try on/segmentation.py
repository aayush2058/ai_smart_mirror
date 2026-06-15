import cv2
import mediapipe as mp
import numpy as np


class PersonSegmenter:

    def __init__(self):

        self.segmenter = mp.solutions.selfie_segmentation.SelfieSegmentation(
            model_selection=1
        )

        # Lower = more body area included
        # Higher = stricter mask
        self.threshold = 0.25

        # -------------------------
        # PERFORMANCE SETTINGS
        # -------------------------
        self.frame_count = 0
        self.last_mask = None

        # Run segmentation every 3 frames
        # 1 = best quality but slower
        # 2 = balanced
        # 3 = faster
        # 4/5 = fastest but mask may lag
        self.process_every = 3

    def get_person_mask(self, frame):

        self.frame_count += 1

        # Reuse previous mask for speed
        if (
            self.last_mask is not None
            and self.frame_count % self.process_every != 0
        ):
            return self.last_mask

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.segmenter.process(rgb)

        if results.segmentation_mask is None:
            return self.last_mask

        mask = results.segmentation_mask

        # Convert soft mask to clear body mask
        mask = (mask > self.threshold).astype(np.uint8) * 255

        # Smooth mask edges
        mask = cv2.GaussianBlur(mask, (15, 15), 0)

        self.last_mask = mask

        return mask

    def keep_overlay_inside_person(self, original_frame, outfit_frame):

        mask = self.get_person_mask(original_frame)

        if mask is None:
            return outfit_frame

        alpha = mask.astype(float) / 255.0
        alpha = alpha[:, :, None]

        outfit_difference = outfit_frame.astype(float) - original_frame.astype(float)

        cleaned_frame = original_frame.astype(float) + outfit_difference * alpha

        return cleaned_frame.astype("uint8")