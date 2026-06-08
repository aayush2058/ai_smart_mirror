import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose

pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ✅ FORCE WINDOWS BACKEND
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# ❗ check if camera opened
if not cap.isOpened():
    print("❌ CAMERA NOT OPENED")
    exit()

def get_frame():

    ret, frame = cap.read()

    if not ret or frame is None:
        print("❌ FRAME FAILED")
        return None, None

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    landmarks = None

    if results and results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

    return frame, landmarks


def release():
    cap.release()