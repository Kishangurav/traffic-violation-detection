# Traffic Violation Detection System

### AI-Powered Real-Time Traffic Monitoring and Violation Verification

A full-stack deep learning and computer vision system for detecting, tracking, verifying, and recording possible traffic violations from video.

## Current Feature Set

| Feature | Status |
| --- | --- |
| YOLOv8 vehicle detection | Live |
| Persistent multi-object tracking | Live |
| Temporal red-light verification | Live |
| Speed estimation | Live |
| Helmet violation detection | Live |
| Evidence screenshots + JSON reports | Live |
| FastAPI backend | Live |
| React dashboard | Live |

### What changed in the high-level upgrade?

The system no longer treats a single frame crossing the stop line as sufficient evidence.

The upgraded pipeline is:

```text
Video
  ↓
YOLOv8 Detection
  ↓
Persistent Vehicle Tracking
  ↓
Temporal Violation Condition
  ↓
Multi-frame Verification
  ↓
Confirmed Violation
  ↓
Evidence + Structured Report
  ↓
FastAPI / React Dashboard
```

### Temporal verification

A tracked vehicle must satisfy the red-light condition for multiple processed frames before the event is recorded. The number of required frames and the cooldown period are configurable in `config.yaml`.

This is intended to reduce single-frame false positives and make violation records more explainable.

## Technology Stack

### Machine Learning and Computer Vision

- **YOLOv8** — object detection.
- **OpenCV** — video processing and visualization.
- **EasyOCR** — license plate text recognition.
- **IoU-based tracking layer** — maintains persistent vehicle IDs across nearby frames.
- **Temporal verification** — confirms rule conditions over multiple frames.

### Backend

- **FastAPI**
- **Uvicorn**
- **PyYAML**

### Frontend

- **React**
- **Vite**
- **Tailwind CSS**
- **Recharts**
- **Axios**

## Quick Start

```bash
git clone https://github.com/Kishangurav/traffic-violation-detection.git
cd traffic-violation-detection

python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

FastAPI:

```powershell
python -m uvicorn api.main:app --reload --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Dashboard:

```text
http://localhost:5173
```

## Project Structure

```text
traffic-violation-detection/
├── main.py
├── config.yaml
├── requirements.txt
├── api/
├── src/
│   ├── detection/
│   ├── tracking/
│   ├── violation/
│   │   ├── red_light.py
│   │   ├── speed_estimator.py
│   │   └── temporal_verifier.py
│   └── utils/
├── frontend/
├── data/
├── output/
└── models/
```

## Important Project Limitation

The current signal is simulated from a configurable time interval. It is not yet detecting the physical traffic signal from the camera feed.

Similarly, speed estimation depends on the calibration points configured for the camera scene.

These are planned areas for the next upgrade rather than claims of production-grade enforcement.

## Project Direction

The long-term goal is to evolve this prototype into an AI-assisted traffic intelligence platform covering:

- temporal violation verification
- explainable evidence
- human review
- traffic-flow analytics
- violation heatmaps
- environmental robustness
- advanced license-plate association
- automated reports

Developed by Kishan Gurav.
