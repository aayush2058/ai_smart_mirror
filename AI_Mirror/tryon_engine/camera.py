import cv2
import mediapipe as mp

from camera_thread import ThreadedCamera


mp_pose = mp.solutions.pose

pose = None
camera = None

frame_count = 0
pose_every = 2
last_landmarks = None


def start_camera():
    global pose, camera, frame_count, last_landmarks

    if camera is not None:
        return

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

    if not camera.running:
        release()
        return False

    frame_count = 0
    last_landmarks = None
    return True


def get_frame():
    global frame_count, last_landmarks, camera, pose

    if camera is None:
        start_camera()

    frame = camera.read()

    if frame is None:
        return None, None

    frame_count += 1

    if frame_count % pose_every == 0 and pose is not None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        if results and results.pose_landmarks:
            last_landmarks = results.pose_landmarks.landmark

    return frame, last_landmarks


def release():
    global camera, pose, last_landmarks

    if camera is not None:
        camera.release()
        camera = None

    if pose is not None:
        pose.close()
        pose = None

    last_landmarks = None
