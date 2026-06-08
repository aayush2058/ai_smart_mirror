import math


class FitEngine:
    """
    Calculates stable body measurements for clothing fitting.
    This keeps fitting logic separate from rendering logic.
    """

    def __init__(self, smoothing=0.35):
        self.smoothing = smoothing
        self.last = None

    def _point(self, landmark, frame_w, frame_h):
        return int(landmark.x * frame_w), int(landmark.y * frame_h)

    def _smooth_value(self, old, new):
        if old is None:
            return new
        return old * (1 - self.smoothing) + new * self.smoothing

    def _distance_x(self, p1, p2):
        return abs(p2[0] - p1[0])

    def measure(self, landmarks, frame_shape):
        h, w = frame_shape[:2]

        ls = self._point(landmarks[11], w, h)
        rs = self._point(landmarks[12], w, h)
        lh = self._point(landmarks[23], w, h)
        rh = self._point(landmarks[24], w, h)
        lk = self._point(landmarks[25], w, h)
        rk = self._point(landmarks[26], w, h)
        la = self._point(landmarks[27], w, h)
        ra = self._point(landmarks[28], w, h)

        shoulder_center = ((ls[0] + rs[0]) // 2, (ls[1] + rs[1]) // 2)
        hip_center = ((lh[0] + rh[0]) // 2, (lh[1] + rh[1]) // 2)
        knee_center = ((lk[0] + rk[0]) // 2, (lk[1] + rk[1]) // 2)
        ankle_center = ((la[0] + ra[0]) // 2, (la[1] + ra[1]) // 2)

        shoulder_width = self._distance_x(ls, rs)
        hip_width = self._distance_x(lh, rh)

        torso_height = abs(hip_center[1] - shoulder_center[1])
        leg_height = abs(ankle_center[1] - hip_center[1])

        waist_y = int(shoulder_center[1] + torso_height * 0.72)
        crotch_y = int(hip_center[1] + leg_height * 0.18)

        measured = {
            "left_shoulder": ls,
            "right_shoulder": rs,
            "left_hip": lh,
            "right_hip": rh,
            "left_knee": lk,
            "right_knee": rk,
            "left_ankle": la,
            "right_ankle": ra,

            "shoulder_center": shoulder_center,
            "hip_center": hip_center,
            "knee_center": knee_center,
            "ankle_center": ankle_center,

            "shoulder_width": shoulder_width,
            "hip_width": hip_width,
            "torso_height": torso_height,
            "leg_height": leg_height,
            "waist_y": waist_y,
            "crotch_y": crotch_y,
        }

        if self.last is None:
            self.last = measured
            return measured

        smoothed = {}

        for key, value in measured.items():
            old = self.last[key]

            if isinstance(value, tuple):
                smoothed[key] = (
                    int(self._smooth_value(old[0], value[0])),
                    int(self._smooth_value(old[1], value[1]))
                )
            else:
                smoothed[key] = int(self._smooth_value(old, value))

        self.last = smoothed
        return smoothed

    def shirt_box(self, body, width_scale, height_scale, vertical_offset, horizontal_offset):
        shoulder_width = body["shoulder_width"]
        hip_width = body["hip_width"]
        shoulder_center = body["shoulder_center"]
        torso_height = body["torso_height"]

        # More stable than shoulder-only width
        natural_width = int((shoulder_width * 0.85) + (hip_width * 0.15))

        width = int(natural_width * width_scale)
        height = int(torso_height * height_scale)

        x = shoulder_center[0] - width // 2 + horizontal_offset
        y = shoulder_center[1] - int(height * vertical_offset)

        return x, y, width, height

    def pants_box(self, body, width_scale, height_scale, vertical_offset, horizontal_offset):
        hip_width = body["hip_width"]
        hip_center = body["hip_center"]
        leg_height = body["leg_height"]

        width = int(hip_width * width_scale)
        height = int(leg_height * height_scale)

        x = hip_center[0] - width // 2 + horizontal_offset
        y = hip_center[1] - int(height * vertical_offset)

        return x, y, width, height