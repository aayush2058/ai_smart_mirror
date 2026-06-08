import cv2
from camera import get_frame

# SIMPLE UI LAYER (you can extend later)
def draw_ui(frame):

    cv2.rectangle(frame, (10, 10), (280, 70), (0, 0, 0), 2)

    cv2.putText(frame, "AI Mirror Mode",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2)

    return frame


while True:

    frame = get_frame()

    if frame is None:
        continue

    # ADD UI HERE (IMPORTANT)
    frame = draw_ui(frame)

    cv2.imshow("AI Mirror", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()