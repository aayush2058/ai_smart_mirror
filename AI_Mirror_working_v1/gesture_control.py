import mediapipe as mp
import math


class GestureController:

    def __init__(self):

        self.hands = mp.solutions.hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    def _get_hands(self, frame):
        return self.hands.process(frame).multi_hand_landmarks

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

            # MediaPipe hand landmark numbers:
            # 4 = thumb tip
            # 8 = index finger tip
            thumb_tip = hand.landmark[4]
            index_tip = hand.landmark[8]

            distance = math.sqrt(
                (thumb_tip.x - index_tip.x) ** 2 +
                (thumb_tip.y - index_tip.y) ** 2
            )

            # Lower value = harder pinch
            # Higher value = easier pinch
            if distance < 0.05:

                pinch_x = int((thumb_tip.x + index_tip.x) / 2 * frame_w)
                pinch_y = int((thumb_tip.y + index_tip.y) / 2 * frame_h)

                return (pinch_x, pinch_y)

        return None