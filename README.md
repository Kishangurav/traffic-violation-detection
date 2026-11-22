# Traffic Violation Detection System

A traffic-monitoring demo for Bangalore. Watch vehicles move through an annotated video in OpenCV, then open the React dashboard to review the events saved by the detector. The traffic signal is simulated, and speed estimates use measurements from the camera’s view of the road.

![Python](https://img.shields.io/badge/Python-blue?style=for-the-badge&logo=python&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Detection-red?style=for-the-badge)
![OpenCV](https://img.shields.io/badge/OpenCV-Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Dashboard-20232A?style=for-the-badge&logo=react)

## Features

| Feature | How it works |
| --- | --- |
| Vehicle detection | YOLOv8 and OpenCV identify and draw boxes around cars, motorcycles, buses and trucks. |
| Vehicle tracking | A custom tracker matches vehicles across frames using bounding-box overlap and the distance between box centers. Each track gets an ID and a trail. |
| Red-light detection | Records a crossing when a tracked vehicle passes the stop line from the approach side while the simulated signal is red. |
| Speed estimation | Maps vehicle positions to road coordinates using camera calibration. Flags vehicles whose estimated speed exceeds the configured limit, which defaults to 50 km/h. |
| Helmet detection | With compatible weights at `models/helmet.pt`, the detector checks motorcycle riders and flags a track after repeated no-helmet detections. This feature is optional. |
| Evidence capture | Saves an annotated screenshot, a JSON report and a SQLite record. Each vehicle track can generate one event of each type per detector run. |
| Dashboard | Shows totals and charts, refreshes statistics every five seconds, and lets you browse violations and filter them by type. |

## How the parts fit together

The detector (`main.py`) reads the video and writes events to `output/violations.db`. FastAPI queries that database through SQLAlchemy and serves saved screenshots. The React frontend uses Axios to request the statistics and violation records, Recharts to draw the charts, and Tailwind CSS for styling.

Dashboard totals include events saved across runs. You can reopen the dashboard after the video ends and still review those events. If the API goes offline after a successful refresh, the updated dashboard keeps the last counts visible and shows a connection warning. For a live view of vehicles and their track IDs, use the detector’s OpenCV window.

## Quick start in VS Code

### 1. Open the project

If you already have the repository, open the folder containing `main.py` in VS Code. For a fresh copy, run:

```bash
git clone https://github.com/Kishangurav/traffic-violation-detection.git
cd traffic-violation-detection
```

### 2. Install dependencies once

The following commands use Windows PowerShell, 64-bit Python 3.11 and Node.js with npm. The frontend supports Node.js 20 from 20.19 onward, or Node.js 22.12 and newer. If you already have a working `venv`, skip the first command.

```powershell
py -3.11 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt fastapi uvicorn "SQLAlchemy>=2,<3" "pydantic>=2,<3"
npm --prefix frontend ci
```

On macOS or Linux, the repository’s requirements file includes Windows-specific packages. For the detector and dashboard, install the runtime dependencies in a virtual environment as follows. Use `./venv/bin/python` in place of `.\venv\Scripts\python.exe` in the launch commands.

```bash
python3.11 -m venv venv
./venv/bin/python -m pip install "ultralytics==8.4.10" opencv-python numpy PyYAML fastapi uvicorn "SQLAlchemy>=2,<3" "pydantic>=2,<3"
npm --prefix frontend ci
```

### 3. Start the API and dashboard

Open two VS Code terminals in the project folder.

**Terminal 1 — FastAPI**

```powershell
.\venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8000
```

Wait for `Application startup complete`. You can check the [health endpoint](http://127.0.0.1:8000/api/v1/health) or open the [interactive API docs](http://127.0.0.1:8000/docs).

**Terminal 2 — React dashboard**

```powershell
cd frontend
npm run dev
```

Open the **Local** URL printed by Vite, usually [http://localhost:5173](http://localhost:5173). A fresh database shows zero violations.

### 4. Run the detector

Open a third terminal in the folder containing `main.py`:

```powershell
.\venv\Scripts\python.exe main.py
```

The default input is `data/raw/traffic.mp4`. The vehicle detector uses `yolov8n.pt`, so allow internet access on the first run if the weights need to download. Watch the annotated video and press **q** in the OpenCV window to stop. New events appear in the dashboard on its next refresh.

## Using a different video

1. Set `video.source` in [config.yaml](config.yaml) to your video path. Set `violation.speed_limit` in km/h and `violation.signal_interval` in seconds.
2. Set the stop line for that view. Click its two endpoints, then click the side vehicles approach from. Press **Enter** to save `stop_line.json`.
3. Calibrate speed for the same view. Mark the four corners of a road rectangle in the order shown, press **Enter**, then enter its real width and length in metres. The script saves `calibration.json`.

Run these commands from the project folder, replacing the example path with yours:

```powershell
.\venv\Scripts\python.exe scripts/set_stop_line.py "data/raw/my-video.mp4"
.\venv\Scripts\python.exe scripts/calibrate_speed.py "data/raw/my-video.mp4"
```

The included calibration files describe the sample view. A change in camera position or video framing requires new measurements. To enable helmet checks, provide a trained helmet model at `models/helmet.pt`. Without it, the detector continues with vehicle tracking, stop-line checks and calibrated speed estimation.

## Project guide

| Path | Purpose |
| --- | --- |
| [main.py](main.py) | Runs video processing and the OpenCV preview. |
| [src/detection/](src/detection/) and [src/tracking/](src/tracking/) | Vehicle and helmet models, track matching and trajectories. |
| [src/violation/](src/violation/) | Stop-line crossing checks and calibrated speed estimates. |
| [src/ptz/](src/ptz/) | Calculates the pan and tilt values shown for a selected vehicle. |
| [src/utils/](src/utils/) | Evidence recording, SQLite storage, configuration and video overlays. |
| [api/](api/) | FastAPI routes and response models. |
| [frontend/](frontend/) | React dashboard, violations table and camera registry. |
| [scripts/](scripts/) | Tools for setting the stop line, calibrating speed and training a helmet model. |
| `output/` | Generated `violations.db`, `screenshots/*.jpg` and `reports/*.json`. |

## API endpoints

All paths below use the prefix `/api/v1`. A **violation ID** identifies one saved event. A **vehicle ID** identifies a track and can recur when the detector restarts.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Check API status. |
| GET | `/stats` | Get total events and counts by type. |
| GET | `/violations` | List recent records. Supports `limit`, `offset` and `violation_type`. |
| GET | `/violations/id/{violation_id}` | Get one event by its database ID. |
| GET | `/violations/{vehicle_id}` | Get the latest saved event for a vehicle ID. |
| GET | `/violations/type/{violation_type}` | Filter by `red_light`, `speeding` or `no_helmet`. |
| DELETE | `/violations/{violation_id}` | In the updated API, delete the single database record matching this ID. |
| GET | `/cameras` | List registered cameras. |
| GET | `/cameras/{camera_id}` | Get one camera entry. |
| POST | `/cameras` | Add a camera entry. |
| DELETE | `/cameras/{camera_id}` | Remove a camera entry. |

Before deleting a violation, check the parameter in [your running API docs](http://127.0.0.1:8000/docs). If the DELETE route shows `{vehicle_id}`, that version deletes **every record with that vehicle ID**. Screenshot and report files stay on disk.

The camera registry is held in memory and resets when the API restarts. The detector reads its active video source from `config.yaml`.

## License

MIT. Developed by [Kishan Gurav](https://github.com/Kishangurav).
