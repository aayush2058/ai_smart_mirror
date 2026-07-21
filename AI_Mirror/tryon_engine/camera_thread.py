import cv2
import mediapipe as mp
import threading
import time


class ThreadedCamera:

    @staticmethod
    def _open_camera(camera_index):
        for backend in (cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY):
            cap = cv2.VideoCapture(camera_index, backend)
            if cap.isOpened():
                return cap
            cap.release()
        return cv2.VideoCapture(camera_index)

    def __init__(self, camera_index=0, width=960, height=540, fps=30):
<<<<<<< HEAD
=======
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        self.last_frame_at = None
        self.frames_received = 0
        self.failed_reads = 0
        self.reconnect_count = 0
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)

        self.cap = self._open_camera(camera_index)

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
<<<<<<< HEAD

            time.sleep(0.001)

=======
                    self.last_frame_at = time.monotonic()
                    self.frames_received += 1
                    self.failed_reads = 0
            else:
                self.failed_reads += 1
                if self.failed_reads >= 30 and self.running:
                    self._reconnect()

            time.sleep(0.001)

    def _reconnect(self):
        if self.cap is not None:
            self.cap.release()
        time.sleep(0.5)
        if not self.running:
            return
        self.cap = self._open_camera(self.camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        self.failed_reads = 0
        self.reconnect_count += 1

    def status(self):
        age = None
        if self.last_frame_at is not None:
            age = round(time.monotonic() - self.last_frame_at, 2)
        return {
            "state": "running" if self.running else "stopped",
            "frames_received": self.frames_received,
            "last_frame_age_seconds": age,
            "reconnect_count": self.reconnect_count,
        }

>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
    def read(self):

        with self.lock:
            if self.frame is None:
                return None

            return self.frame.copy()

    def release(self):

        self.running = False

<<<<<<< HEAD
        if self.cap is not None:
            self.cap.release()
=======
        if getattr(self, "thread", None) is not None and self.thread.is_alive():
            self.thread.join(timeout=2)

        if self.cap is not None:
            self.cap.release()
            self.cap = None
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
