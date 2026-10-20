import os
import shutil
import sys

from roboflow import Roboflow
from ultralytics import YOLO

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ENV_FILE = os.path.join(ROOT, ".env")


def read_key():
    key = os.environ.get("ROBOFLOW_API_KEY")
    if key:
        return key.strip()

    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ROBOFLOW_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def find_dataset(workspace, project_id, version):
    """Reuse the downloaded dataset if it is already on disk."""
    for name in os.listdir(ROOT):
        folder = os.path.join(ROOT, name)
        if os.path.isfile(os.path.join(folder, "data.yaml")) and name.lower().startswith("helmet-detection"):
            return folder

    api_key = read_key()
    if not api_key:
        raise SystemExit("Roboflow key not found in the environment or in .env")

    rf = Roboflow(api_key=api_key)
    project = rf.workspace(workspace).project(project_id)
    return project.version(version).download("yolov8").location


def main():
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage: python scripts\\train_helmet.py <workspace> <project> <version>"
        )

    workspace, project_id, version = sys.argv[1], sys.argv[2], int(sys.argv[3])

    dataset_dir = find_dataset(workspace, project_id, version)
    data_yaml = os.path.join(dataset_dir, "data.yaml")
    print("Dataset folder:", dataset_dir)

    model = YOLO("yolov8n.pt")
    model.train(data=data_yaml, epochs=30, imgsz=640, batch=16, device=0, workers=0)

    best = os.path.join(model.trainer.save_dir, "weights", "best.pt")
    os.makedirs(os.path.join(ROOT, "models"), exist_ok=True)
    shutil.copy(best, os.path.join(ROOT, "models", "helmet.pt"))
    print("Saved models/helmet.pt")


if __name__ == "__main__":
    main()