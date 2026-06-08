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
        # True  = show landmarks, body centre, mode, hands, pinch dot
        # False = clean product/demo view
        self.debug = False

        # -------------------------
        # MENU TOGGLE SETTINGS
        # -------------------------
        self.last_menu_toggle_time = 0
        self.menu_toggle_cooldown = 1.2

        self.two_palm_ready = True
        self.last_two_palm_seen = 0

        # -------------------------
        # PINCH CLICK SETTINGS
        # -------------------------
        self.last_pinch_time = 0
        self.pinch_cooldown = 1.0

    def run(self):

        while True:

            # -------------------------
            # CAMERA FRAME
            # -------------------------
            frame, landmarks = get_frame()

            if frame is None:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            now = time.time()

            # -------------------------
            # GESTURE DETECTION
            # -------------------------
            palms = self.gesture.get_palm_count(rgb)
            pinch_pos = self.gesture.get_pinch_position(rgb, frame.shape)

            # -------------------------
            # TWO PALM MENU TOGGLE
            # -------------------------
            if palms == 2:
                self.last_two_palm_seen = now

                if (
                    self.two_palm_ready
                    and now - self.last_menu_toggle_time > self.menu_toggle_cooldown
                ):
                    self.menu_open = not self.menu_open
                    self.last_menu_toggle_time = now
                    self.two_palm_ready = False

            else:
                if now - self.last_two_palm_seen > 0.6:
                    self.two_palm_ready = True

            # -------------------------
            # BODY TRACKING + OUTFIT
            # -------------------------
            if landmarks is not None:
                self.view_mode = self.body.get_body_orientation(landmarks)

                if self.debug:
                    frame = self.body.draw_landmarks(frame, landmarks)

                    center = self.body.get_shoulder_center(landmarks, frame)
                    frame = self.body.draw_body_center(frame, center)

                frame = self.clothes.draw_shirt(
                    frame,
                    landmarks,
                    self.view_mode
                )

            # -------------------------
            # UI DATA
            # -------------------------
            ui_data = {
                "groups": self.clothes.get_menu_groups(),
                "selected_group": self.clothes.selected_group,
                "outfit_selected": self.clothes.has_outfit()
            }

            # -------------------------
            # DRAW UI
            # -------------------------
            frame = self.ui.render(frame, self.menu_open, ui_data)

            # -------------------------
            # PINCH ON MENU OPTIONS
            # -------------------------
            if self.menu_open:
                clicked_group = self.ui.get_clicked_group(pinch_pos)

                if (
                    clicked_group is not None
                    and now - self.last_pinch_time > self.pinch_cooldown
                ):

                    if clicked_group == "Remove Outfit":
                        self.clothes.remove_outfit()

                    else:
                        self.clothes.set_group(clicked_group)

                    self.menu_open = False
                    self.last_pinch_time = now

            # -------------------------
            # PINCH ON NEXT ARROW BUTTON
            # -------------------------
            clicked_arrow = self.ui.is_point_inside_next_arrow(pinch_pos)

            if (
                clicked_arrow
                and now - self.last_pinch_time > self.pinch_cooldown
            ):
                self.clothes.next_cloth()
                self.last_pinch_time = now

            # -------------------------
            # PRODUCT INFO
            # -------------------------
            current_product = self.clothes.get_current_product()

            if current_product is not None:
                frame = self.ui.draw_product_info(
                    frame,
                    current_product,
                    self.clothes.selected_group
                )

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

            # -------------------------
            # SHOW FINAL FRAME
            # -------------------------
            cv2.imshow("SMART MIRROR", frame)

            # -------------------------
            # KEYBOARD CONTROLS
            # -------------------------
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q') or key == ord('Q'):
                break

            elif key == ord('n') or key == ord('N'):
                self.clothes.next_cloth()

            elif key == ord('p') or key == ord('P'):
                self.clothes.previous_cloth()

            elif key == ord('r') or key == ord('R'):
                self.clothes.remove_outfit()

            elif key == ord('d') or key == ord('D'):
                self.debug = not self.debug

            elif key == ord('m') or key == ord('M'):
                self.menu_open = not self.menu_open

            elif key == ord('c') or key == ord('C'):
                self.clothes.save_config()

            # -------------------------
            # LIVE FIT CALIBRATION KEYS
            # -------------------------
            elif key == ord('w') or key == ord('W'):
                self.clothes.increase_width()

            elif key == ord('s') or key == ord('S'):
                self.clothes.decrease_width()

            elif key == ord('l') or key == ord('L'):
                self.clothes.increase_height()

            elif key == ord('j') or key == ord('J'):
                self.clothes.decrease_height()

            elif key == ord('i') or key == ord('I'):
                self.clothes.move_up()

            elif key == ord('k') or key == ord('K'):
                self.clothes.move_down()

        release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    SmartMirror().run()