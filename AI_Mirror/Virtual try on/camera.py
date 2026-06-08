import cv2
import mediapipe as mp

from camera_thread import ThreadedCamera


mp_pose = mp.solutions.pose

pose = mp_pose.Pose(
    model_complexity=0,
    smooth_landmarks=True,
    enable_segmentation=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

camera = ThreadedCamera(
    camera_index=0,
    width=960,
    height=540,
    fps=30
)

# -------------------------
# POSE PERFORMANCE SETTINGS
# -------------------------
frame_count = 0
pose_every = 2
last_landmarks = None


def get_frame():

    global frame_count, last_landmarks

    frame = camera.read()

    if frame is None:
        return None, None

    frame_count += 1

    if frame_count % pose_every == 0:

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        if results and results.pose_landmarks:
            last_landmarks = results.pose_landmarks.landmark

    return frame, last_landmarks


def release():
    camera.release()