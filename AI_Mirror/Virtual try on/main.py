import cv2
import time

from camera import get_frame, release
from bodytracking import BodyTracker
from gesture_control import GestureController
from clothing_overlay import ClothingOverlay
from overlay_ui import MirrorUI
from segmentation import PersonSegmenter


class SmartMirror:

    def __init__(self):

        self.body = BodyTracker()
        self.gesture = GestureController()
        self.clothes = ClothingOverlay()
        self.ui = MirrorUI()
        self.segmenter = PersonSegmenter()

        self.menu_open = False
        self.view_mode = "FRONT"

        # Debug mode
        self.debug = False

        # Segmentation
        self.use_segmentation = False

        # Freeze mode
        self.freeze_mode = False
        self.frozen_frame = None
        self.frozen_landmarks = None

        # FPS
        self.prev_time = time.time()
        self.fps = 0

        # Menu toggle
        self.last_menu_toggle_time = 0
        self.menu_toggle_cooldown = 1.2
        self.two_palm_ready = True
        self.last_two_palm_seen = 0

        # Pinch cooldown
        self.last_pinch_time = 0
        self.pinch_cooldown = 1.0

        # Mouse click
        self.mouse_click_pos = None

        # developer mode / customer mode switch
        self.customer_mode = False

    # For mouse control
    def mouse_callback(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:
            self.mouse_click_pos = (x, y)


    def run(self):

        cv2.namedWindow("SMART MIRROR")
        cv2.setMouseCallback("SMART MIRROR", self.mouse_callback)

        while True:

            # -------------------------
            # CAMERA FRAME
            # -------------------------
            live_frame, live_landmarks = get_frame()

            if live_frame is None:
                continue

            # -------------------------
            # FREEZE MODE
            # -------------------------
            if self.freeze_mode and self.frozen_frame is not None:
                frame = self.frozen_frame.copy()
                landmarks = self.frozen_landmarks
            else:
                frame = live_frame.copy()
                landmarks = live_landmarks

                self.frozen_frame = live_frame.copy()
                self.frozen_landmarks = live_landmarks

            now = time.time()

            # -------------------------
            # GESTURE DETECTION
            # Gestures come from live camera even in freeze mode.
            # -------------------------
            live_rgb = cv2.cvtColor(live_frame, cv2.COLOR_BGR2RGB)

            # New optimized gesture controller
            self.gesture.update(live_rgb, live_frame.shape)
            palms = self.gesture.get_palm_count()
            pinch_pos = self.gesture.get_pinch_position()

            # For mouse
            click_pos = pinch_pos

            if self.mouse_click_pos is not None:
                click_pos = self.mouse_click_pos
                self.mouse_click_pos = None
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
            # BODY TRACKING + OUTFITS
            # -------------------------
            if landmarks is not None:
                self.view_mode = self.body.get_body_orientation(landmarks)
                
                self.view_mode = "FRONT"

                if self.debug:
                    frame = self.body.draw_landmarks(frame, landmarks)

                    center = self.body.get_shoulder_center(landmarks, frame)
                    frame = self.body.draw_body_center(frame, center)

                # Save clean frame before outfits
                original_frame = frame.copy()

                # Draw pants and shirt on the SAME frame
                frame = self.clothes.draw_outfits(
                    frame,
                    landmarks,
                    self.view_mode
                )

                # Apply segmentation once to final combined outfit frame
                if self.use_segmentation and self.clothes.has_outfit():
                    frame = self.segmenter.keep_overlay_inside_person(
                        original_frame,
                        frame
                    )

            # -------------------------
            # UI DATA
            # -------------------------
            ui_data = {
                "groups": self.clothes.get_menu_groups(),
                "active_group": self.clothes.active_group,
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
                clicked_group = self.ui.get_clicked_group(click_pos)

                if (
                    clicked_group is not None
                    and now - self.last_pinch_time > self.pinch_cooldown
                ):
                    self.clothes.set_group(clicked_group)

                    self.menu_open = False
                    self.last_pinch_time = now

            # -------------------------
            # PINCH ON NEXT ARROW BUTTON
            # -------------------------
            clicked_arrow = self.ui.is_point_inside_next_arrow(click_pos)

            if (
                clicked_arrow
                and now - self.last_pinch_time > self.pinch_cooldown
            ):
                self.clothes.next_cloth()
                self.last_pinch_time = now

            # -------------------------
            # OUTFIT PRODUCT INFO
            # -------------------------
            selected_products = self.clothes.get_selected_products()
            frame = self.ui.draw_outfit_info(frame, selected_products, self.clothes, self.customer_mode)

            # -------------------------
            # DEBUG FEEDBACK
            # -------------------------
            if self.debug and not self.customer_mode:
                frame = self.ui.draw_gesture_feedback(
                    frame,
                    palms,
                    self.view_mode,
                    pinch_pos
                )

            # -------------------------
            # FPS DISPLAY
            # -------------------------
            current_time = time.time()
            self.fps = 1 / (current_time - self.prev_time)
            self.prev_time = current_time

            if not self.customer_mode:
                cv2.putText(
                    frame,
                    f"FPS: {int(self.fps)}",
                    (30, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2
                )

            # -------------------------
            # FREEZE / SEGMENTATION LABELS
            # -------------------------
            if self.freeze_mode:
                cv2.putText(
                    frame,
                    "FREEZE MODE",
                    (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 255),
                    2
                )

            if not self.use_segmentation:
                cv2.putText(
                    frame,
                    "SEG OFF",
                    (30, 140),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
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
                self.clothes.remove_all()

            elif key == ord('d') or key == ord('D'):
                self.debug = not self.debug

            elif key == ord('m') or key == ord('M'):
                self.menu_open = not self.menu_open

            elif key == ord('g') or key == ord('G'):
                self.use_segmentation = not self.use_segmentation
                print("Segmentation:", self.use_segmentation)

            elif key == ord('z') or key == ord('Z'):
                self.freeze_mode = not self.freeze_mode
                print("Freeze mode:", self.freeze_mode)

            elif key == ord('t') or key == ord('T'):
                cv2.imwrite("test_frame.jpg", frame)
                print("✅ Test frame saved as test_frame.jpg")

            elif key == ord('c') or key == ord('C'):
                self.clothes.save_config()

            elif key == ord('v') or key == ord('V'):
                self.clothes.save_current_product_fit()
                print("this cloth adjusted in catalogue ✅")

            elif key == ord('u') or key == ord('U'): # customer mode toggle
                self.customer_mode = not self.customer_mode
                print("Customer mode:", self.customer_mode)

            # -------------------------
            # LIVE FIT CALIBRATION KEYS
            # Uses active group:
            # active_group = Shirts → changes shirt
            # active_group = Pants  → changes pants
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

            elif key == ord('a') or key == ord('A'):
                self.clothes.move_left()

            elif key == ord('f') or key == ord('F'):
                self.clothes.move_right()

        release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    SmartMirror().run()