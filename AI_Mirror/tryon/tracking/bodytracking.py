import cv2


class BodyTracker:

    def __init__(self):
        self.current_mode = "FRONT"
        self.pending_mode = "FRONT"
        self.mode_counter = 0
        self.mode_stability_frames = 5

    def get_landmarks(self, results):
        return results

    def draw_landmarks(self, frame, landmarks):

        if landmarks is None:
            return frame

        h, w = frame.shape[:2]

        for idx, lm in enumerate(landmarks):

            x = int(lm.x * w)
            y = int(lm.y * h)

            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

            cv2.putText(frame, str(idx), (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                        (255, 255, 255), 1)

        return frame

    def get_shoulder_center(self, landmarks, frame):

        if landmarks is None:
            return None

        h, w = frame.shape[:2]

        ls = landmarks[11]
        rs = landmarks[12]

        cx = int((ls.x + rs.x) / 2 * w)
        cy = int((ls.y + rs.y) / 2 * h)

        return (cx, cy)

    def draw_body_center(self, frame, center):

        if center is None:
            return frame

        cv2.circle(frame, center, 8, (0, 0, 255), -1)

        return frame


    def get_body_orientation(self, landmarks):

        if landmarks is None:
            return self.current_mode

        ls = landmarks[11]
        rs = landmarks[12]
        nose = landmarks[0]

        shoulder_dist = abs(ls.x - rs.x)

        # -----------------------
        # RAW MODE DETECTION
        # -----------------------
        detected_mode = "FRONT"

        if shoulder_dist < 0.10:
            detected_mode = "SIDE"

        elif nose.z > 0.15:
            detected_mode = "BACK"

        else:
            detected_mode = "FRONT"

        # -----------------------
        # MODE STABILITY LOGIC
        # -----------------------
        if detected_mode == self.pending_mode:
            self.mode_counter += 1
        else:
            self.pending_mode = detected_mode
            self.mode_counter = 1

        if self.mode_counter >= self.mode_stability_frames:
            self.current_mode = self.pending_mode

        return self.current_mode