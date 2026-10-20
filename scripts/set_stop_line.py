import json
import os
import sys

import cv2
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT_FILE = os.path.join(ROOT, "stop_line.json")

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
LABELS = ["1 line start", "2 line end", "3 vehicles come from here"]


def redraw():
    img = cv2.resize(frame, None, fx=scale, fy=scale)
    pts = [(int(x * scale), int(y * scale)) for x, y in points]
    for i, p in enumerate(pts):
        cv2.circle(img, p, 6, (0, 0, 255), -1)
        cv2.putText(img, LABELS[i], (p[0] + 8, p[1] - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    if len(pts) >= 2:
        cv2.line(img, pts[0], pts[1], (0, 0, 255), 3)
    cv2.imshow("Stop line", img)


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(points) < 3:
        points.append((x / scale, y / scale))
        redraw()


print("Click 3 points:")
print("  1 and 2 = two ends of the stop line, across the road")
print("  3 = a spot on the road BEFORE the line (where vehicles come from)")
print("Keys: r = reset, Enter = save (after 3 points), q = quit")

cv2.namedWindow("Stop line")
cv2.setMouseCallback("Stop line", on_mouse)
redraw()

while True:
    key = cv2.waitKey(50) & 0xFF
    if key == ord("q"):
        cv2.destroyAllWindows()
        raise SystemExit("Cancelled")
    if key == ord("r"):
        points.clear()
        redraw()
    if key in (13, 10) and len(points) == 3:
        break

cv2.destroyAllWindows()

data = {
    "p1": [float(points[0][0]), float(points[0][1])],
    "p2": [float(points[1][0]), float(points[1][1])],
    "approach_point": [float(points[2][0]), float(points[2][1])],
    "frame_size": [w, h],
}

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Saved", OUT_FILE)