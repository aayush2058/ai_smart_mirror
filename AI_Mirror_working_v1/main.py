import cv2
import time

from camera import get_frame, release
from bodytracking import BodyTracker
from gesture_control import GestureController
from clothing_overlay import ClothingOverlay
from overlay_ui import MirrorUI


class SmartMirror:

    def __init__(self):

        self.body = BodyTracker()
        self.gesture = GestureController()
        self.clothes = ClothingOverlay()
        self.ui = MirrorUI()

        self.menu_open = False
        self.view_mode = "FRONT"

        # Debug mode:
        # True  = show landmarks, numbers, red centre dot, feedback text
        # False = clean product/demo view
        self.debug = False

        # -------------------------
        # MENU TOGGLE SETTINGS
        # -------------------------
        self.last_menu_toggle_time = 0
        self.menu_toggle_cooldown = 1.2

        # Prevent holding two palms from repeatedly opening/closing menu
        self.two_palm_ready = True
        self.last_two_palm_seen = 0

        # -------------------------
        # PINCH CLICK SETTINGS
        # -------------------------
        self.last_pinch_time = 0
        self.pinch_cooldown = 1.0

    def run(self):

        while True:

            frame, landmarks = get_frame()

            if frame is None:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            now = time.time()

            palms = self.gesture.get_palm_count(rgb)
            pinch_pos = self.gesture.get_pinch_position(rgb, frame.shape)

            # -------------------------
            # TWO PALM MENU TOGGLE
            # -------------------------
            if palms == 2:
                self.last_two_palm_seen = now

                if self.two_palm_ready and now - self.last_menu_toggle_time > self.menu_toggle_cooldown:
                    self.menu_open = not self.menu_open
                    self.last_menu_toggle_time = now
                    self.two_palm_ready = False

            else:
                # User must remove the two-palm gesture briefly
                # before two palms can toggle the menu again
                if now - self.last_two_palm_seen > 0.6:
                    self.two_palm_ready = True

            # -------------------------
            # BODY TRACKING + CLOTHING
            # -------------------------
            if landmarks is not None:
                self.view_mode = self.body.get_body_orientation(landmarks)

                if self.debug:
                    frame = self.body.draw_landmarks(frame, landmarks)

                    center = self.body.get_shoulder_center(landmarks, frame)
                    frame = self.body.draw_body_center(frame, center)

                frame = self.clothes.draw_shirt(frame, landmarks, self.view_mode)

            # -------------------------
            # UI
            # -------------------------
            frame = self.ui.render(frame, self.menu_open, None)

            # -------------------------
            # PINCH ON FIT CHANGE BUTTON
            # -------------------------
            clicked_fit_change = self.ui.is_point_inside_fit_change(pinch_pos)

            if clicked_fit_change and now - self.last_pinch_time > self.pinch_cooldown:
                self.clothes.next_cloth()
                self.last_pinch_time = now

            # -------------------------
            # DEBUG FEEDBACK
            # -------------------------
            if self.debug:
                frame = self.ui.draw_gesture_feedback(
                    frame,
                    palms,
                    self.view_mode,
                    pinch_pos
                )

            cv2.imshow("SMART MIRROR", frame)

            # -------------------------
            # KEYBOARD CONTROLS
            # -------------------------
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break

            elif key == ord('n'):
                self.clothes.next_cloth()

            elif key == ord('p'):
                self.clothes.previous_cloth()

            elif key == ord('d'):
                self.debug = not self.debug

            elif key == ord('m'):
                self.menu_open = not self.menu_open

        release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    SmartMirror().run()