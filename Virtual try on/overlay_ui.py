import cv2


class MirrorUI:

    def __init__(self):

        self.group_buttons = {}
        self.next_arrow_button = None

    def render(self, frame, menu_open, data=None):

        outfit_selected = False

        if data is not None:
            outfit_selected = data.get("outfit_selected", False)

        # Show arrow after any outfit is selected and menu is closed
        if outfit_selected and not menu_open:
            frame = self.draw_next_arrow_button(frame)
        else:
            self.next_arrow_button = None

        if menu_open:

            h, w = frame.shape[:2]

            menu_width = 380
            menu_height = 500

            menu_center_x = int(w * 0.75)
            menu_center_y = int(h * 0.45)

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
                active_group = data.get("active_group", None)

                frame = self.draw_group_buttons(
                    frame,
                    groups,
                    active_group,
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

    def draw_group_buttons(self, frame, groups, active_group, menu_x1, menu_y1):

        self.group_buttons = {}

        button_width = 270
        button_height = 45

        x1 = menu_x1 + 55
        y_start = menu_y1 + 125

        for i, group in enumerate(groups):

            y1 = y_start + i * 58
            x2 = x1 + button_width
            y2 = y1 + button_height

            self.group_buttons[group] = (x1, y1, x2, y2)

            if group == active_group:
                border_colour = (0, 255, 255)
                text_colour = (0, 255, 255)
            else:
                border_colour = (255, 255, 255)
                text_colour = (255, 255, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), border_colour, 2)

            cv2.putText(frame, group.upper(),
                        (x1 + 18, y1 + 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
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


    def draw_outfit_info(self, frame, products, clothes=None, customer_mode=False):

        if products is None:
            return frame

        shirt = products.get("shirt")
        pants = products.get("pants")
        active_group = products.get("active_group")

        if shirt is None and pants is None:
            return frame

        h, w = frame.shape[:2]

        # Smaller box for customer mode
        if customer_mode:
            panel_width = 420
            panel_height = 145
        else:
            panel_width = 520
            panel_height = 210

        x1 = 30
        y1 = h - panel_height - 35
        x2 = x1 + panel_width
        y2 = y1 + panel_height

        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.35, frame, 0.65, 0)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

        cv2.putText(
            frame,
            "CURRENT OUTFIT",
            (x1 + 18, y1 + 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 255),
            2
        )

        # Shirt info
        if shirt is not None:
            shirt_name = shirt.get("name", "Unknown Shirt")
            shirt_price = shirt.get("price", "£--")
            shirt_text = f"Shirt: {shirt_name}  {shirt_price}"
        else:
            shirt_text = "Shirt: None"

        cv2.putText(
            frame,
            shirt_text[:50],
            (x1 + 18, y1 + 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (255, 255, 255),
            1
        )

        # Pants info
        if pants is not None:
            pants_name = pants.get("name", "Unknown Pants")
            pants_price = pants.get("price", "£--")
            pants_text = f"Pants: {pants_name}  {pants_price}"
        else:
            pants_text = "Pants: None"

        cv2.putText(
            frame,
            pants_text[:50],
            (x1 + 18, y1 + 92),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (255, 255, 255),
            1
        )

        # CUSTOMER MODE STOPS HERE
        if customer_mode:
            cv2.putText(
                frame,
                "Pinch or tap arrow to change",
                (x1 + 18, y1 + 122),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.42,
                (0, 255, 255),
                1
            )
            return frame

        # Developer-only info below
        if clothes is not None and active_group is not None:

            if active_group == "Pants":
                width = clothes.pants_width_scale
                height = clothes.pants_height_scale
                vertical = clothes.pants_vertical_offset
                horizontal = clothes.pants_horizontal_offset
            else:
                width = clothes.shirt_width_scale
                height = clothes.shirt_height_scale
                vertical = clothes.shirt_vertical_offset
                horizontal = clothes.shirt_horizontal_offset

            active_text = f"Active: {active_group}"
            fit_text = f"Fit: W {width:.2f} | H {height:.2f} | Y {vertical:.2f} | X {horizontal}"

        else:
            active_text = "Active: None"
            fit_text = "Fit: -"

        cv2.putText(
            frame,
            active_text,
            (x1 + 18, y1 + 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (0, 255, 255),
            1
        )

        cv2.putText(
            frame,
            fit_text,
            (x1 + 18, y1 + 152),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (255, 255, 255),
            1
        )

        cv2.putText(
            frame,
            "W/S Width   L/J Height   I/K UpDown   A/F LeftRight   V Save",
            (x1 + 18, y1 + 182),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.40,
            (0, 255, 255),
            1
        )

        return frame
    # Backward-compatible method
    def draw_product_info(self, frame, product, selected_group=None):

        if product is None:
            return frame

        products = {
            "shirt": product if selected_group == "Shirts" else None,
            "pants": product if selected_group == "Pants" else None,
            "active_group": selected_group
        }

        return self.draw_outfit_info(frame, products)

    def draw_gesture_feedback(self, frame, palms, mode, pinch_pos=None):

        overlay = frame.copy()

        cv2.rectangle(overlay, (20, 120), (360, 285), (0, 0, 0), -1)

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
    
    
    def draw_fit_editor(self, frame, clothes):

        if clothes is None:
            return frame

        if clothes.active_group is None:
            return frame

        h, w = frame.shape[:2]

        panel_width = 360
        panel_height = 230

        x1 = 30
        y1 = 140
        x2 = x1 + panel_width
        y2 = y1 + panel_height

        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.35, frame, 0.65, 0)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

        cv2.putText(frame, "FIT EDITOR", (x1 + 20, y1 + 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 255), 2)

        cv2.putText(frame, f"Active: {clothes.active_group}", (x1 + 20, y1 + 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1)

        if clothes.active_group == "Pants":
            width = clothes.pants_width_scale
            height = clothes.pants_height_scale
            vertical = clothes.pants_vertical_offset
            horizontal = clothes.pants_horizontal_offset
        else:
            width = clothes.shirt_width_scale
            height = clothes.shirt_height_scale
            vertical = clothes.shirt_vertical_offset
            horizontal = clothes.shirt_horizontal_offset

        cv2.putText(frame, f"Width: {width:.2f}", (x1 + 20, y1 + 95),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1)

        cv2.putText(frame, f"Height: {height:.2f}", (x1 + 20, y1 + 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1)

        cv2.putText(frame, f"Vertical: {vertical:.2f}", (x1 + 20, y1 + 145),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1)

        cv2.putText(frame, f"Horizontal: {horizontal}", (x1 + 20, y1 + 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1)

        cv2.putText(frame, "W/S Width | L/J Height", (x1 + 20, y1 + 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                    (0, 255, 255), 1)

        cv2.putText(frame, "I/K UpDown | A/F LeftRight | V Save", (x1 + 20, y1 + 220),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42,
                    (0, 255, 255), 1)

        return frame