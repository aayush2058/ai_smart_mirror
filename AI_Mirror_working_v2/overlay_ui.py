import cv2


class MirrorUI:

    def __init__(self):

        self.group_buttons = {}
        self.next_arrow_button = None

    def render(self, frame, menu_open, data=None):

        selected_group = None
        outfit_selected = False

        if data is not None:
            selected_group = data.get("selected_group", None)
            outfit_selected = data.get("outfit_selected", False)

        # -------------------------
        # DRAW NEXT ARROW BUTTON
        # -------------------------
        # Show arrow only after an outfit is selected and menu is closed.
        if outfit_selected and selected_group == "Shirts" and not menu_open:
            frame = self.draw_next_arrow_button(frame)
        else:
            self.next_arrow_button = None

        # -------------------------
        # MENU PANEL
        # -------------------------
        if menu_open:

            h, w = frame.shape[:2]

            menu_width = 360
            menu_height = 380

            # Menu centre at 75% of screen width
            menu_center_x = int(w * 0.75)
            menu_center_y = int(h * 0.42)

            x1 = menu_center_x - menu_width // 2
            y1 = menu_center_y - menu_height // 2
            x2 = menu_center_x + menu_width // 2
            y2 = menu_center_y + menu_height // 2

            x1 = max(10, x1)
            y1 = max(10, y1)
            x2 = min(w - 10, x2)
            y2 = min(h - 10, y2)

            overlay = frame.copy()

            cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 0), -1)

            frame = cv2.addWeighted(overlay, 0.35, frame, 0.65, 0)

            cv2.putText(frame, "MENU", (x1 + 40, y1 + 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 255), 2)

            cv2.putText(frame, "Select Option",
                        (x1 + 40, y1 + 95),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                        (255, 255, 255), 1)

            if data is not None:
                groups = data.get("groups", [])
                selected_group = data.get("selected_group", None)

                frame = self.draw_group_buttons(
                    frame,
                    groups,
                    selected_group,
                    x1,
                    y1
                )

            cv2.putText(frame, "Pinch to select",
                        (x1 + 35, y2 - 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 1)

            cv2.putText(frame, "Two palms = Open/Close",
                        (x1 + 35, y2 - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 1)

        return frame

    def draw_group_buttons(self, frame, groups, selected_group, menu_x1, menu_y1):

        self.group_buttons = {}

        button_width = 250
        button_height = 50

        x1 = menu_x1 + 55
        y_start = menu_y1 + 125

        for i, group in enumerate(groups):

            y1 = y_start + i * 65
            x2 = x1 + button_width
            y2 = y1 + button_height

            self.group_buttons[group] = (x1, y1, x2, y2)

            if group == selected_group:
                border_colour = (0, 255, 255)
                text_colour = (0, 255, 255)
            else:
                border_colour = (255, 255, 255)
                text_colour = (255, 255, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), border_colour, 2)

            cv2.putText(frame, group.upper(),
                        (x1 + 25, y1 + 34),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.65,
                        text_colour,
                        2)

        return frame

    def draw_next_arrow_button(self, frame):

        h, w = frame.shape[:2]

        button_width = 120
        button_height = 70

        margin_right = 45
        margin_bottom = 45

        x1 = w - button_width - margin_right
        y1 = h - button_height - margin_bottom
        x2 = w - margin_right
        y2 = h - margin_bottom

        self.next_arrow_button = (x1, y1, x2, y2)

        overlay = frame.copy()

        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 0), -1)

        frame = cv2.addWeighted(overlay, 0.35, frame, 0.65, 0)

        cv2.rectangle(frame, (x1, y1), (x2, y2),
                      (0, 255, 255), 2)

        cv2.putText(frame, "-->",
                    (x1 + 25, y1 + 47),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (255, 255, 255),
                    2)

        return frame

    def get_clicked_group(self, point):

        if point is None:
            return None

        px, py = point

        for group, box in self.group_buttons.items():

            x1, y1, x2, y2 = box

            if x1 <= px <= x2 and y1 <= py <= y2:
                return group

        return None

    def is_point_inside_next_arrow(self, point):

        if point is None or self.next_arrow_button is None:
            return False

        px, py = point
        x1, y1, x2, y2 = self.next_arrow_button

        return x1 <= px <= x2 and y1 <= py <= y2

    def draw_product_info(self, frame, product, selected_group=None):

        if product is None:
            return frame

        h, w = frame.shape[:2]

        panel_width = 360
        panel_height = 190

        x1 = 30
        y1 = h - panel_height - 40
        x2 = x1 + panel_width
        y2 = y1 + panel_height

        overlay = frame.copy()

        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 0), -1)

        frame = cv2.addWeighted(overlay, 0.35, frame, 0.65, 0)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

        cv2.putText(frame, "CURRENT FIT", (x1 + 20, y1 + 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 255), 2)

        cv2.putText(frame, f"Type: {selected_group}",
                    (x1 + 20, y1 + 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1)

        cv2.putText(frame, product.get("name", "Unknown Product"),
                    (x1 + 20, y1 + 95),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1)

        cv2.putText(frame, product.get("price", "£--"),
                    (x1 + 20, y1 + 125),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (255, 255, 255), 1)

        cv2.putText(frame, f'Colour: {product.get("colour", "N/A")}',
                    (x1 + 20, y1 + 155),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1)

        return frame

    def draw_gesture_feedback(self, frame, palms, mode, pinch_pos=None):

        overlay = frame.copy()

        cv2.rectangle(overlay, (20, 120), (330, 270), (0, 0, 0), -1)

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