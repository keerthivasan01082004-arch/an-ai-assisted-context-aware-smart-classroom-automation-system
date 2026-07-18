# 🏫 Smart Classroom AI — Real-Time Intelligent Room Management System

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-purple)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?logo=opencv)
![License](https://img.shields.io/badge/License-MIT-yellow)

A patent-grade AI-powered smart classroom system that performs **real-time occupancy detection**, **face recognition attendance**, **environment monitoring**, and **automated device control** — all through a live web dashboard.

---

## 📸 Screenshots

> Dashboard with live camera feed, real-time metrics, AI insights, and device controls.

---

## ✨ Features

- 🎥 **Live Camera Feed** — Streams from IP Webcam (mobile) or USB webcam
- 👥 **YOLOv8 Person Detection** — Counts students in real time
- 🧠 **Face Recognition Attendance** — Automatically marks present students by name
- 📊 **Real-Time Dashboard** — 9 live metric cards updating every 3 seconds
- 🌡️ **Environment Monitoring** — Temperature, CO₂, humidity, noise, air quality
- ⚡ **Energy Analytics** — kWh consumption, cost (₹), CO₂ emissions, savings %
- 📅 **Timetable Management** — Upload, edit, and view weekly class schedule
- 🤖 **AI Recommendations** — Context-aware suggestions for energy saving
- 🔧 **Manual Device Control** — Override lights, fan, AC from dashboard
- 📤 **Export Reports** — Download attendance as Excel, stats as CSV or PDF
- 🔮 **Predictive Analytics** — Next class info, occupancy trends, attention status
- 🚨 **Anomaly Detection** — Alerts for unusual patterns

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask |
| Computer Vision | OpenCV, YOLOv8 (Ultralytics) |
| Face Recognition | `face-recognition` + `dlib` |
| OCR | Tesseract (`pytesseract`) |
| Frontend | HTML, CSS, JavaScript (Vanilla) |
| Reports | ReportLab (PDF), OpenPyXL (Excel) |
| Camera | IP Webcam Pro (Android) / USB webcam |

---

## 📦 Requirements

### System Requirements
- Python 3.11
- Tesseract OCR installed → [Download here](https://github.com/UB-Mannheim/tesseract/wiki)
- A camera: USB webcam **or** Android phone running [IP Webcam Pro](https://play.google.com/store/apps/details?id=com.pas.webcam.pro)

### Python Packages

```bash
pip install -r requirements.txt
```

**`requirements.txt` contents:**

```
flask
opencv-python
pytesseract
ultralytics
torch
torchvision
reportlab
openpyxl
face-recognition
dlib
numpy
```

> ⚠️ `dlib` requires CMake and C++ build tools on Windows.
> Install Visual Studio Build Tools before running `pip install dlib`.

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Ravishankarsubramani27/Smartclassroom_realtime.git
cd Smartclassroom_realtime
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download YOLOv8 model

The model downloads automatically on first run. Or manually:

```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### 5. Configure camera

Edit `modules/camera_module.py` and set your camera URL:

```python
# For IP Webcam (Android phone)
CAMERA_URL = "http://<YOUR_PHONE_IP>:8080/video"

# For built-in/USB webcam
CAMERA_URL = 0
```

### 6. Run the application

```bash
python app.py
```

### 7. Open in browser

| Page | URL |
|------|-----|
| 🏠 Dashboard | http://localhost:5000 |
| 📅 Timetable | http://localhost:5000/timetable |
| 📋 Attendance | http://localhost:5000/attendance |
| 🧑 Face Enroll | http://localhost:5000/face/enroll |

---

## 📁 Project Structure

```
Smartclassroom_realtime/
│
├── app.py                   # Flask app — all routes
├── state.py                 # Shared real-time state object
├── requirements.txt
├── timetable_map.json       # Weekly timetable data
├── students.json            # Student registry
│
├── modules/
│   ├── camera_module.py     # Camera capture + YOLO detection (threaded)
│   ├── face_recognition_module.py  # Face enrollment & recognition
│   ├── ocr_module.py        # Timetable OCR parsing
│   ├── realtime_engine.py   # Background AI loop (sensors, energy, alerts)
│   └── __init__.py
│
├── templates/               # HTML pages
│   ├── dashboard.html
│   ├── timetable.html
│   ├── timetable_editor.html
│   ├── attendance.html
│   └── face_enroll.html
│
├── static/
│   ├── style.css
│   └── timetable.png
│
└── face_database/           # Enrolled student face images
    └── <STUDENT_ID>.jpg
```

---

## 🎓 Face Recognition Setup

1. Go to **http://localhost:5000/face/enroll**
2. Enter the student's ID and name
3. Click **Capture** to take a photo via the live camera
4. The system encodes and saves the face automatically
5. The student will be recognized and marked present in future sessions

---

## 📅 Timetable Setup

1. Go to **http://localhost:5000/timetable/editor**
2. Add your class schedule (day, time, subject, venue, type)
3. Click **Save** — the system immediately uses it for predictions and context

---

## 📤 Export Options

| Format | What it contains |
|--------|-----------------|
| 📊 CSV | All real-time metrics and daily statistics |
| 📄 PDF | Professional formatted report with tables |
| 📋 Excel | Attendance sheet with student list, timestamps, summary |

---

## ⚙️ Configuration

| File | What to configure |
|------|------------------|
| `modules/camera_module.py` | Camera URL / source |
| `timetable_map.json` | Weekly class schedule |
| `students.json` | Student ID and name registry |
| `state.py` | Initial sensor values |

---

## 🔧 Troubleshooting

| Problem | Fix |
|---------|-----|
| Black camera feed | Check phone IP, ensure IPWebcam server is started |
| `dlib` install fails | Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) first |
| PDF export error | `pip install reportlab` |
| Tesseract not found | Set path in `ocr_module.py` or add to system PATH |
| Face not recognized | Re-enroll in better lighting, closer to camera |

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

**Ravishankar Subramani**  
GitHub: [@Ravishankarsubramani27](https://github.com/Ravishankarsubramani27)

---

> 🏆 Built as a patent-grade intelligent classroom system combining computer vision, AI, and IoT automation.
