import mediapipe as mp
import math


class GestureController:

    def __init__(self):

        self.hands = mp.solutions.hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

    def _get_hands(self, frame):
        results = self.hands.process(frame)
        return results.multi_hand_landmarks

    def _is_palm_open(self, hand):

        tips = [8, 12, 16, 20]
        folded = 0

        for t in tips:
            if hand.landmark[t].y > hand.landmark[t - 2].y:
                folded += 1

        return folded <= 1

    def get_palm_count(self, frame):

        hands = self._get_hands(frame)

        if not hands:
            return 0

        return sum(self._is_palm_open(h) for h in hands)

    def get_pinch_position(self, frame, frame_shape):

        hands = self._get_hands(frame)

        if not hands:
            return None

        frame_h, frame_w = frame_shape[:2]

        for hand in hands:

            thumb_tip = hand.landmark[4]
            index_tip = hand.landmark[8]

            # Convert thumb and index position to pixels
            thumb_x = int(thumb_tip.x * frame_w)
            thumb_y = int(thumb_tip.y * frame_h)

            index_x = int(index_tip.x * frame_w)
            index_y = int(index_tip.y * frame_h)

            # Pixel distance between thumb and index finger
            distance = math.sqrt(
                (thumb_x - index_x) ** 2 +
                (thumb_y - index_y) ** 2
            )

            # Pinch centre position
            pinch_x = (thumb_x + index_x) // 2
            pinch_y = (thumb_y + index_y) // 2

            # Increase this if pinch is still hard
            if distance < 30:
                return (pinch_x, pinch_y)

        return None