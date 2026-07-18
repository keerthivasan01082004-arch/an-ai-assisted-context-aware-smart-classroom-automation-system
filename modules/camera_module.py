import cv2
import time
import threading
import numpy as np
import urllib.request
from ultralytics import YOLO
from state import state

# ── Optional face recognition ──────────────────────────────────────────────
try:
    from modules.face_recognition_module import face_recognition_system
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    print("⚠️ Face recognition not available.")
    FACE_RECOGNITION_AVAILABLE = False
    face_recognition_system = None

# ── Camera source ───────────────────────────────────────────────────────────
CAMERA_URL      = "http://192.168.31.251:8080/video"     # MJPEG stream
CAMERA_SHOT_URL = "http://192.168.31.251:8080/shot.jpg"  # JPEG snapshot fallback
# CAMERA_URL = 0  # Built-in webcam

# ── YOLO model ──────────────────────────────────────────────────────────────
model = YOLO("yolov8n.pt")

# ── Camera control state ────────────────────────────────────────────────────
camera_zoom  = 1.0
camera_pan_x = 0
camera_pan_y = 0
use_face_recognition = FACE_RECOGNITION_AVAILABLE

def set_camera_zoom(zoom_level):
    global camera_zoom
    camera_zoom = max(1.0, min(3.0, zoom_level))

def set_camera_pan(pan_x, pan_y):
    global camera_pan_x, camera_pan_y
    camera_pan_x, camera_pan_y = pan_x, pan_y

def reset_camera():
    global camera_zoom, camera_pan_x, camera_pan_y
    camera_zoom, camera_pan_x, camera_pan_y = 1.0, 0, 0

# ── Shared frame buffer (thread-safe) ───────────────────────────────────────
_lock           = threading.Lock()
_latest_jpeg    = None   # latest encoded JPEG bytes ready to stream
_capture_thread = None
_thread_running = False

# ── Internal helpers ─────────────────────────────────────────────────────────

def _apply_zoom_and_pan(frame):
    """Rotate 180° (fix upside-down) then crop/zoom."""
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    if camera_zoom == 1.0 and camera_pan_x == 0 and camera_pan_y == 0:
        return frame
    h, w = frame.shape[:2]
    nw, nh = int(w / camera_zoom), int(h / camera_zoom)
    cx = min(max(w // 2 + camera_pan_x, nw // 2), w - nw // 2)
    cy = min(max(h // 2 + camera_pan_y, nh // 2), h - nh // 2)
    x1, y1 = cx - nw // 2, cy - nh // 2
    cropped = frame[y1:y1+nh, x1:x1+nw]
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)


def _annotate(frame, boxes_data):
    """Draw pre-computed detection boxes + overlays onto the frame."""
    for (x1, y1, x2, y2, label, color) in boxes_data:
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.putText(frame, f"Students: {state['people']}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Zoom: {camera_zoom:.1f}x", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    mode = "Face Recognition" if use_face_recognition else "Person Detection"
    cv2.putText(frame, mode, (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    return frame


def _run_detection(frame):
    """
    Run YOLO or face recognition on a SMALL copy of the frame.
    Returns (boxes_data, count, attendance_list).
    Runs in the background thread — never blocks the stream.
    """
    # Downscale to 320px wide for faster inference
    h, w = frame.shape[:2]
    scale = 320 / w
    small = cv2.resize(frame, (320, int(h * scale)))

    boxes_data = []

    if use_face_recognition and face_recognition_system is not None:
        try:
            annotated, recognized = face_recognition_system.recognize_faces(frame)
            if recognized:
                unique = {s['id']: s for s in recognized}
                attendance = list(unique.values())
                count = len(attendance)
            else:
                results = model(small, verbose=False)[0]
                count = sum(1 for b in results.boxes
                            if model.names[int(b.cls[0])] == "person")
                attendance = [
                    {"id": f"Unknown_{i+1:03d}",
                     "name": f"Unknown Person {i+1}",
                     "confidence": 0.0}
                    for i in range(count)
                ]
        except Exception:
            count, attendance = 0, []
    else:
        results = model(small, verbose=False)[0]
        count = 0
        attendance = []
        inv_scale = 1.0 / scale
        for box in results.boxes:
            if model.names[int(box.cls[0])] == "person":
                count += 1
                sx1, sy1, sx2, sy2 = map(int, box.xyxy[0])
                # Scale coords back to original frame size
                x1 = int(sx1 * inv_scale)
                y1 = int(sy1 * inv_scale)
                x2 = int(sx2 * inv_scale)
                y2 = int(sy2 * inv_scale)
                conf = float(box.conf[0])
                boxes_data.append((x1, y1, x2, y2, f"Person {conf:.2f}", (0, 255, 0)))
                attendance.append({"id": f"Student_{count:03d}",
                                   "name": f"Student_{count:03d}",
                                   "confidence": conf})

    return boxes_data, count, attendance


# ── Background capture + detection thread ───────────────────────────────────

def _capture_loop():
    """
    Runs in a daemon thread.
    Captures frames from IPWebcam, runs detection every N frames,
    and writes the annotated JPEG into _latest_jpeg.
    """
    global _latest_jpeg, _thread_running

    DETECT_EVERY = 5        # run YOLO every 5th frame (lighter CPU load)
    TARGET_FPS   = 15       # target stream fps
    FRAME_DELAY  = 1.0 / TARGET_FPS

    frame_count   = 0
    last_boxes    = []
    consecutive_failures = 0

    # ── Try MJPEG first ──
    print(f"📹 Trying MJPEG: {CAMERA_URL}")
    cap = cv2.VideoCapture(CAMERA_URL)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    use_mjpeg = False
    if cap.isOpened():
        for _ in range(8):
            ret, tf = cap.read()
            if ret and tf is not None and tf.mean() > 1.0:
                use_mjpeg = True
                print("✅ MJPEG stream OK")
                break
        if not use_mjpeg:
            print("⚠️  MJPEG black — using /shot.jpg polling")
            cap.release()
    else:
        print("⚠️  MJPEG failed — using /shot.jpg polling")

    state["camera_online"] = True

    while _thread_running:
        t_start = time.time()
        frame = None

        # ── Grab frame ──
        if use_mjpeg and cap.isOpened():
            ret, frame = cap.read()
            if not ret or frame is None or frame.mean() < 0.5:
                consecutive_failures += 1
                if consecutive_failures > 15:
                    print("❌ MJPEG lost — falling back to /shot.jpg")
                    cap.release()
                    use_mjpeg = False
                    consecutive_failures = 0
                time.sleep(0.05)
                continue
            consecutive_failures = 0
        else:
            try:
                with urllib.request.urlopen(CAMERA_SHOT_URL, timeout=2) as resp:
                    arr = np.frombuffer(resp.read(), dtype=np.uint8)
                    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            except Exception:
                pass

            if frame is None:
                consecutive_failures += 1
                state["camera_online"] = False
                time.sleep(0.3)
                continue
            consecutive_failures = 0
            state["camera_online"] = True

        frame_count += 1

        # ── Apply spatial transforms ──
        frame = _apply_zoom_and_pan(frame)

        # ── Run detection on every Nth frame ──
        if frame_count % DETECT_EVERY == 0:
            try:
                last_boxes, count, attendance = _run_detection(frame)
                state["people"]     = count
                state["attendance"] = attendance
            except Exception as e:
                print(f"⚠️  Detection error: {e}")

        # ── Annotate & encode ──
        display = _annotate(frame.copy(), last_boxes)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 55]
        ok, buf = cv2.imencode(".jpg", display, encode_param)
        if ok:
            with _lock:
                _latest_jpeg = buf.tobytes()

        # ── Pace to TARGET_FPS ──
        elapsed = time.time() - t_start
        sleep_time = FRAME_DELAY - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

    if use_mjpeg:
        cap.release()
    print("🛑 Camera capture thread stopped.")


def _ensure_capture_thread():
    """Start the background capture thread if it's not already running."""
    global _capture_thread, _thread_running
    if _capture_thread is None or not _capture_thread.is_alive():
        _thread_running = True
        _capture_thread = threading.Thread(target=_capture_loop, daemon=True)
        _capture_thread.start()
        print("🚀 Camera capture thread started.")


# ── Public stream generator (called by Flask) ────────────────────────────────

def generate_frames():
    """
    Non-blocking generator: just reads _latest_jpeg and yields it.
    All heavy work happens in the background thread.
    """
    _ensure_capture_thread()

    # Wait up to 5 s for first frame
    for _ in range(50):
        with _lock:
            if _latest_jpeg is not None:
                break
        time.sleep(0.1)

    while True:
        with _lock:
            jpeg = _latest_jpeg

        if jpeg:
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" +
                   jpeg + b"\r\n")
        time.sleep(1.0 / 15)  # stream at 15 fps max
