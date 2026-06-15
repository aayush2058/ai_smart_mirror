import mediapipe as mp
import math


class GestureController:

    def __init__(self):

        self.hands = mp.solutions.hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

        # -------------------------
        # PERFORMANCE SETTINGS
        # -------------------------
        self.frame_count = 0
        self.process_every = 2

        self.last_hands = None
        self.last_palm_count = 0
        self.last_pinch_position = None

    def update(self, frame, frame_shape):

        self.frame_count += 1

        # Reuse previous hand result for speed
        if self.frame_count % self.process_every != 0:
            return

        results = self.hands.process(frame)
        hands = results.multi_hand_landmarks

        self.last_hands = hands

        if not hands:
            self.last_palm_count = 0
            self.last_pinch_position = None
            return

        self.last_palm_count = sum(self._is_palm_open(h) for h in hands)
        self.last_pinch_position = self._calculate_pinch_position(
            hands,
            frame_shape
        )

    def _is_palm_open(self, hand):

        tips = [8, 12, 16, 20]
        folded = 0

        for t in tips:
            if hand.landmark[t].y > hand.landmark[t - 2].y:
                folded += 1

        return folded <= 1

    def _calculate_pinch_position(self, hands, frame_shape):

        frame_h, frame_w = frame_shape[:2]

        for hand in hands:

            thumb_tip = hand.landmark[4]
            index_tip = hand.landmark[8]

            thumb_x = int(thumb_tip.x * frame_w)
            thumb_y = int(thumb_tip.y * frame_h)

            index_x = int(index_tip.x * frame_w)
            index_y = int(index_tip.y * frame_h)

            distance = math.sqrt(
                (thumb_x - index_x) ** 2 +
                (thumb_y - index_y) ** 2
            )

            pinch_x = (thumb_x + index_x) // 2
            pinch_y = (thumb_y + index_y) // 2

            if distance < 45:
                return (pinch_x, pinch_y)

        return None

    def get_palm_count(self):
        return self.last_palm_count

    def get_pinch_position(self):
        return self.last_pinch_position