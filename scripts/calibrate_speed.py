import json
import os
import sys

import cv2
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT_FILE = os.path.join(ROOT, "calibration.json")

video = sys.argv[1] if len(sys.argv) > 1 else "data/raw/traffic.mp4"
frame_no = int(sys.argv[2]) if len(sys.argv) > 2 else 0

cap = cv2.VideoCapture(video)
cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
ok, frame = cap.read()
cap.release()
if not ok:
    raise SystemExit(f"Cannot read frame {frame_no} from {video}")

h, w = frame.shape[:2]
scale = min(1.0, 1280 / w, 720 / h)
points = []
LABELS = ["1 near-left", "2 near-right", "3 far-right", "4 far-left"]


def redraw():
    img = cv2.resize(frame, None, fx=scale, fy=scale)
    for i, (x, y) in enumerate(points):
        p = (int(x * scale), int(y * scale))
        cv2.circle(img, p, 6, (0, 0, 255), -1)
        cv2.putText(img, LABELS[i], (p[0] + 8, p[1] - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    if len(points) > 1:
        pts = np.array([(int(x * scale), int(y * scale)) for x, y in points], np.int32)
        cv2.polylines(img, [pts], len(points) == 4, (0, 255, 0), 2)
    cv2.imshow("Calibrate", img)


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
        points.append((x / scale, y / scale))
        redraw()


print("Click 4 corners of a rectangle ON THE ROAD SURFACE, in this order:")
print("  1 near-left, 2 near-right, 3 far-right, 4 far-left")
print("Keys: r = reset, Enter = confirm (after 4 points), q = quit")

cv2.namedWindow("Calibrate")
cv2.setMouseCallback("Calibrate", on_mouse)
redraw()

while True:
    key = cv2.waitKey(50) & 0xFF
    if key == ord("q"):
        cv2.destroyAllWindows()
        raise SystemExit("Cancelled")
    if key == ord("r"):
        points.clear()
        redraw()
    if key in (13, 10) and len(points) == 4:
        break

cv2.destroyAllWindows()

width_m = float(input("Real width in meters between points 1 and 2 (e.g. 7 for two lanes): "))
length_m = float(input("Real length in meters between points 1 and 4 (e.g. 12): "))

image_points = [[float(x), float(y)] for x, y in points]
world_points = [[0, 0], [width_m, 0], [width_m, length_m], [0, length_m]]

H = cv2.getPerspectiveTransform(np.float32(image_points), np.float32(world_points))
back = cv2.perspectiveTransform(np.float32([image_points]), H)[0]
print("Check (should match world points):", back.round(2).tolist())

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        {
            "video": video,
            "frame_size": [w, h],
            "image_points": image_points,
            "world_points": world_points,
            "width_m": width_m,
            "length_m": length_m,
        },
        f,
        indent=2,
    )
print("Saved", OUT_FILE)