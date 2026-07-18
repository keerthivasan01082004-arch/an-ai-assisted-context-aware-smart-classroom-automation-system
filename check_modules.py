import ast
import sys
import os

files = [
    'app.py',
    'state.py',
    'modules/camera_module.py',
    'modules/realtime_engine.py',
    'modules/ocr_module.py',
    'modules/face_recognition_module.py'
]

print("=" * 50)
print("SYNTAX CHECK")
print("=" * 50)
all_ok = True
for f in files:
    try:
        with open(f, encoding='utf-8') as fh:
            ast.parse(fh.read())
        print(f"OK  {f}")
    except SyntaxError as e:
        print(f"SYNTAX ERROR  {f}  line {e.lineno}: {e.msg}")
        all_ok = False
    except Exception as e:
        print(f"ERROR  {f}: {e}")
        all_ok = False

print("=" * 50)

# Check installed packages
print("\nPACKAGE CHECK")
print("=" * 50)
packages = {
    'flask': 'flask',
    'cv2': 'opencv-python',
    'pytesseract': 'pytesseract',
    'ultralytics': 'ultralytics',
    'torch': 'torch',
    'reportlab': 'reportlab',
    'openpyxl': 'openpyxl',
    'numpy': 'numpy',
}
for mod, pkg in packages.items():
    try:
        __import__(mod)
        print(f"OK  {pkg}")
    except ImportError:
        print(f"MISSING  {pkg}  --> pip install {pkg}")

# Optional packages
optional = {
    'face_recognition': 'face-recognition',
    'dlib': 'dlib',
}
print("\nOPTIONAL PACKAGES")
for mod, pkg in optional.items():
    try:
        __import__(mod)
        print(f"OK  {pkg}")
    except ImportError:
        print(f"NOT INSTALLED  {pkg} (optional - face recognition disabled)")

# Check key files exist
print("\nFILE CHECK")
print("=" * 50)
key_files = [
    'timetable_map.json',
    'static/timetable.png',
    'yolov8n.pt',
    'face_encodings.pkl',
    'students.json',
]
for kf in key_files:
    if os.path.exists(kf):
        print(f"OK  {kf}")
    else:
        print(f"MISSING  {kf}")

# Check Tesseract
print("\nTESSERACT CHECK")
print("=" * 50)
tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(tesseract_path):
    print(f"OK  Tesseract found at {tesseract_path}")
else:
    print(f"MISSING  Tesseract not found at {tesseract_path}")
    print("         OCR disabled by default so app still works without it")

print("\n" + "=" * 50)
print("CHECK COMPLETE")
print("=" * 50)
