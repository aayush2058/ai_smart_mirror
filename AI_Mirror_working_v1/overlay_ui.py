import cv2


class MirrorUI:

    def __init__(self):

        # Button position will be calculated dynamically
        self.fit_change_button = None

    def render(self, frame, menu_open, _):
        # -------------------------
        # ALWAYS DRAW FIT CHANGE BUTTON
        # -------------------------
        frame = self.draw_fit_change_button(frame)

        # -------------------------
        # MENU PANEL
        # -------------------------
        if menu_open:

            h, w = frame.shape[:2]

            # Menu size
            menu_width = 300
            menu_height = 380

            # Menu centre at 75% of screen width
            menu_center_x = int(w * 0.75)
            menu_center_y = int(h * 0.35)

            x1 = menu_center_x - menu_width // 2
            y1 = menu_center_y - menu_height // 2
            x2 = menu_center_x + menu_width // 2
            y2 = menu_center_y + menu_height // 2

            # Keep menu inside screen
            x1 = max(10, x1)
            y1 = max(10, y1)
            x2 = min(w - 10, x2)
            y2 = min(h - 10, y2)

            overlay = frame.copy()

            # Transparent menu panel
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 0), -1)

            frame = cv2.addWeighted(overlay, 0.35, frame, 0.65, 0)

            cv2.putText(frame, "MENU", (x1 + 40, y1 + 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 255), 2)

            cv2.putText(frame, "Two palms = Open/Close",
                        (x1 + 30, y1 + 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 1)

            cv2.putText(frame, "Pinch FIT CHANGE button",
                        (x1 + 30, y1 + 170),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 1)

        return frame

    def draw_fit_change_button(self, frame):

        h, w = frame.shape[:2]

        # -------------------------
        # BOTTOM RIGHT BUTTON
        # -------------------------
        button_width = 230
        button_height = 65

        margin_right = 40
        margin_bottom = 40

        x1 = w - button_width - margin_right
        y1 = h - button_height - margin_bottom
        x2 = w - margin_right
        y2 = h - margin_bottom

        self.fit_change_button = (x1, y1, x2, y2)

        # Transparent background for button
        overlay = frame.copy()

        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 0), -1)

        frame = cv2.addWeighted(overlay, 0.35, frame, 0.65, 0)

        # Button border
        cv2.rectangle(frame, (x1, y1), (x2, y2),
                      (0, 255, 255), 2)

        # Button text
        cv2.putText(frame, "FIT CHANGE",
                    (x1 + 25, y1 + 42),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2)

        return frame

    def is_point_inside_fit_change(self, point):

        if point is None or self.fit_change_button is None:
            return False

        px, py = point
        x1, y1, x2, y2 = self.fit_change_button

        return x1 <= px <= x2 and y1 <= py <= y2

    def draw_gesture_feedback(self, frame, palms, mode, pinch_pos=None):

        overlay = frame.copy()

        cv2.rectangle(overlay, (20, 120), (310, 260), (0, 0, 0), -1)

        alpha = 0.4
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

        cv2.putText(frame, f"Mode: {mode}", (40, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 255), 1)

        cv2.putText(frame, f"Hands: {palms}", (40, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 0), 1)

        if pinch_pos is not None:
            cv2.putText(frame, f"Pinch: {pinch_pos}", (40, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 1)

            cv2.circle(frame, pinch_pos, 8, (255, 0, 255), -1)

        return frame