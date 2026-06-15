import cv2
import mediapipe as mp
import threading
import time


class ThreadedCamera:

    def __init__(self, camera_index=0, width=960, height=540, fps=30):

        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)

        if not self.cap.isOpened():
            print("❌ CAMERA NOT OPENED")
            self.running = False
            return

        self.running = True
        self.frame = None

        self.lock = threading.Lock()

        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):

        while self.running:

            ret, frame = self.cap.read()

            if ret and frame is not None:
                frame = cv2.flip(frame, 1)

                with self.lock:
                    self.frame = frame

            time.sleep(0.001)

    def read(self):

        with self.lock:
            if self.frame is None:
                return None

            return self.frame.copy()

    def release(self):

        self.running = False

        if self.cap is not None:
            self.cap.release()