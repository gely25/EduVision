import threading
import time
import cv2
from src.infrastructure.ai_models import object_detector

camera_thread = None
camera_active = False


def camera_loop():
    """Captura continua de frames y actualiza detección de objetos."""
    global camera_active
    print("🎥 Iniciando hilo de cámara...")

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ No se pudo acceder a la cámara.")
        camera_active = False
        return

    print("✅ Cámara iniciada correctamente.")

    while camera_active:
        success, frame = cap.read()
        if not success:
            print("⚠️ No se pudo leer frame.")
            break

        # 🔹 Detectar objetos y guardar frame
        object_detector.detect_objects(frame)

        time.sleep(0.02)

    cap.release()
    print("🟢 Cámara detenida correctamente.")


def start_camera():
    """Inicia la cámara en un hilo separado."""
    global camera_thread, camera_active
    if not camera_active:
        camera_active = True
        camera_thread = threading.Thread(target=camera_loop, daemon=True)
        camera_thread.start()
        print("▶️ Cámara iniciada.")


def stop_camera():
    """Detiene la cámara y libera recursos."""
    global camera_active, camera_thread
    camera_active = False
    if camera_thread is not None:
        camera_thread.join(timeout=1)
        camera_thread = None
    print("⏹️ Cámara detenida.")


def gen_frames():
    """Genera frames en formato MJPEG."""
    while camera_active:
        with object_detector.frame_lock:
            if object_detector.last_frame is not None:
                ret, buffer = cv2.imencode('.jpg', object_detector.last_frame)
                if not ret:
                    continue
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                time.sleep(0.05)


def get_base64_frame():
    """Devuelve el último frame como imagen codificada en base64."""
    with object_detector.frame_lock:
        if object_detector.last_frame is None:
            print("⚠️ No hay frame disponible todavía.")
            return None
        ret, buffer = cv2.imencode('.jpg', object_detector.last_frame)
        if not ret:
            print("⚠️ Error al codificar frame.")
            return None
        import base64
        encoded = base64.b64encode(buffer).decode('utf-8')
        print("📸 Frame enviado al frontend.")
        return f"data:image/jpeg;base64,{encoded}"
