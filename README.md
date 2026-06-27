<div align="center">

# 🚦 Traffic Violation Detection System

### AI-Powered Real-Time Traffic Enforcement for Bangalore

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Detection-red?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react)
![OpenCV](https://img.shields.io/badge/OpenCV-Vision-5C3EE8?style=for-the-badge&logo=opencv)

</div>

---

## 🎯 Overview

A full-stack deep learning system that detects traffic violations in real time using computer vision. Built specifically for Bangalore traffic enforcement.

## ✅ Features

| Feature | Status |
|---|---|
| 🚗 Vehicle Detection (YOLOv8) | ✅ Live |
| 🔴 Red Light Violation | ✅ Live |
| ⚡ Speed Estimation | ✅ Live |
| 🪖 Helmet Detection | ✅ Live |
| 📸 Evidence Capture (Screenshot + JSON) | ✅ Live |
| 📊 Live React Dashboard | ✅ Live |
| 🔌 FastAPI REST Backend | ✅ Live |
| 🎯 Multi-Object Tracking | ✅ Live |

## 🏗️ System Architecture

```
Video Input → YOLOv8 Detection → Multi-Object Tracker
     → Violation Engine (Red Light / Speed / Helmet)
     → Evidence Recorder (Screenshot + JSON)
     → FastAPI Backend → React Dashboard
```

## 🛠️ Tech Stack

**ML & Computer Vision**
- YOLOv8 — Vehicle detection
- OpenCV — Frame processing
- EasyOCR — License plate reading
- ByteTrack — Multi-object tracking

**Backend**
- FastAPI — REST API
- Uvicorn — ASGI server
- PyYAML — Config management

**Frontend**
- React + Vite
- Tailwind CSS
- Recharts — Data visualization
- Axios — API calls

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/traffic-violation-detection.git
cd traffic-violation-detection
```

### 2. Setup Python environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

### 3. Run detection engine
```bash
python main.py
```

### 4. Run API server
```bash
python -m uvicorn api.main:app --reload --port 8000
```

### 5. Run frontend
```bash
cd frontend
npm install
npm run dev
```

### 6. Open dashboard
```
http://localhost:5173
```

## 📁 Project Structure

```
traffic-violation-detection/
├── main.py                  # Entry point
├── config.yaml              # All settings
├── requirements.txt
├── api/                     # FastAPI backend
│   ├── main.py
│   ├── routes.py
│   └── models.py
├── src/
│   ├── detection/
│   │   ├── detector.py      # YOLOv8 vehicle detection
│   │   ├── helmet_detector.py
│   │   └── plate_detector.py
│   ├── tracking/
│   │   └── tracker.py       # Multi-object tracking
│   ├── violation/
│   │   ├── red_light.py     # Red light detection
│   │   └── speed_estimator.py
│   └── utils/
│       ├── recorder.py      # Evidence saving
│       ├── dashboard.py     # OpenCV overlay
│       └── config.py
├── frontend/                # React dashboard
│   └── src/
│       └── pages/
│           ├── Dashboard.jsx
│           ├── Violations.jsx
│           └── Cameras.jsx
├── data/
│   └── raw/                 # Input videos
├── output/
│   ├── screenshots/         # Violation images
│   └── reports/             # JSON reports
└── models/                  # ML model weights
```

## 📊 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/violations` | Get all violations |
| GET | `/api/v1/violations/{id}` | Get violation by ID |
| GET | `/api/v1/violations/type/{type}` | Filter by type |
| DELETE | `/api/v1/violations/{id}` | Delete violation |
| GET | `/api/v1/cameras` | Get all cameras |
| POST | `/api/v1/cameras` | Add new camera |
| GET | `/api/v1/stats` | Get dashboard stats |
| GET | `/api/v1/health` | Health check |

## 🌆 Built for Bangalore

Designed to address Bangalore's top traffic violations:
- 🔴 Red light jumping at major junctions
- ⚡ Speeding on ORR and flyovers
- 🪖 Helmet violations on two-wheelers
- 🚫 Wrong-way driving on one-way roads

## 📄 License

MIT License — free to use and modify.

---

<div align="center">
Made with ❤️ for Bangalore Traffic Safety
</div>