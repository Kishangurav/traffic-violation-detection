# Traffic Violation Detection System

### AI-Powered Real-Time Traffic Enforcement for Bangalore

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge\&logo=python)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Detection-red?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?style=for-the-badge\&logo=fastapi)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge\&logo=react)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-5C3EE8?style=for-the-badge\&logo=opencv)

---

## Overview

A full-stack deep learning and computer vision system designed to detect and monitor traffic violations in real time. The platform integrates object detection, multi-object tracking, violation analysis, and evidence collection with a FastAPI backend and React dashboard.

The system is designed to support traffic monitoring and enforcement scenarios in Bangalore.

## Features

| Feature                                         | Status |
| ----------------------------------------------- | ------ |
| Vehicle Detection using YOLOv8                  | Live   |
| Red Light Violation Detection                   | Live   |
| Vehicle Speed Estimation                        | Live   |
| Helmet Violation Detection                      | Live   |
| Evidence Capture (Screenshots and JSON Reports) | Live   |
| Real-Time React Dashboard                       | Live   |
| FastAPI REST Backend                            | Live   |
| Multi-Object Tracking                           | Live   |

## System Architecture

```text
Video Input
     |
     v
YOLOv8 Object Detection
     |
     v
Multi-Object Tracking
     |
     v
Violation Detection Engine
(Red Light / Speed / Helmet)
     |
     v
Evidence Recording
(Screenshots + JSON Reports)
     |
     v
FastAPI Backend
     |
     v
React Dashboard
```

## Technology Stack

### Machine Learning and Computer Vision

* **YOLOv8** — Object detection for identifying vehicles and traffic-related objects.
* **OpenCV** — Video processing, frame analysis, and computer vision operations.
* **EasyOCR** — License plate text recognition.
* **ByteTrack** — Multi-object tracking across video frames.

### Backend

* **FastAPI** — REST API development.
* **Uvicorn** — ASGI server for running the backend.
* **PyYAML** — Configuration management.

### Frontend

* **React** — User interface development.
* **Vite** — Frontend development and build tooling.
* **Tailwind CSS** — UI styling.
* **Recharts** — Data visualization.
* **Axios** — HTTP communication with backend services.

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Kishangurav/traffic-violation-detection.git
cd traffic-violation-detection
```

### 2. Set Up the Python Environment

```bash
python -m venv venv
```

#### Windows

```bash
venv\Scripts\activate
```

#### macOS / Linux

```bash
source venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Run the Detection Engine

```bash
python main.py
```

### 4. Start the FastAPI Backend

```bash
python -m uvicorn api.main:app --reload --port 8000
```

### 5. Start the Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

### 6. Access the Dashboard

```text
http://localhost:5173
```

## Project Structure

```text
traffic-violation-detection/
|
├── main.py                  # Application entry point
├── config.yaml              # System configuration
├── requirements.txt         # Python dependencies
|
├── api/                     # FastAPI backend
│   ├── main.py
│   ├── routes.py
│   └── models.py
|
├── src/
│   ├── detection/
│   │   ├── detector.py      # YOLOv8 vehicle detection
│   │   ├── helmet_detector.py
│   │   └── plate_detector.py
│   │
│   ├── tracking/
│   │   └── tracker.py       # Multi-object tracking
│   │
│   ├── violation/
│   │   ├── red_light.py     # Red light violation detection
│   │   └── speed_estimator.py
│   │
│   └── utils/
│       ├── recorder.py      # Evidence recording
│       ├── dashboard.py     # OpenCV visualization
│       └── config.py        # Configuration utilities
|
├── frontend/                # React frontend
│   └── src/
│       └── pages/
│           ├── Dashboard.jsx
│           ├── Violations.jsx
│           └── Cameras.jsx
|
├── data/
│   └── raw/                 # Input video files
|
├── output/
│   ├── screenshots/         # Violation evidence images
│   └── reports/             # JSON violation reports
|
└── models/                  # Machine learning model weights
```

## API Endpoints

| Method | Endpoint                         | Description                      |
| ------ | -------------------------------- | -------------------------------- |
| GET    | `/api/v1/violations`             | Retrieve all recorded violations |
| GET    | `/api/v1/violations/{id}`        | Retrieve a violation by ID       |
| GET    | `/api/v1/violations/type/{type}` | Filter violations by type        |
| DELETE | `/api/v1/violations/{id}`        | Delete a recorded violation      |
| GET    | `/api/v1/cameras`                | Retrieve registered cameras      |
| POST   | `/api/v1/cameras`                | Register a new camera            |
| GET    | `/api/v1/stats`                  | Retrieve dashboard statistics    |
| GET    | `/api/v1/health`                 | Check backend health status      |

## Application Scope

The system focuses on traffic violations commonly observed in Bangalore, including:

* Red light violations at signalized intersections.
* Speeding on major roads and flyovers.
* Helmet violations involving two-wheelers.
* Wrong-way driving on one-way roads.

## Key Capabilities

* Real-time object detection and tracking.
* Automated traffic violation identification.
* Evidence generation through screenshots and structured reports.
* Backend API integration for violation management.
* Interactive dashboard for monitoring traffic events.
* Modular architecture for extending detection capabilities.

## License

This project is licensed under the MIT License.

---

Developed by [Kishan Gurav](https://github.com/Kishangurav)
