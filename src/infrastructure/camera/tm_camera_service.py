import os
import cv2
import threading
import time
import numpy as np
import base64
import tensorflow as tf
from keras.layers import TFSMLayer

# ======================================
# ⚙️ Cargar modelo Teachable Machine
# ======================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "infrastructure", "ai_models", "teachable_machine", "model.savedmodel")

print("🔍 Intentando cargar modelo desde:", MODEL_PATH)
print("📁 Existe?", os.path.exists(MODEL_PATH))

try:
    model = TFSMLayer(MODEL_PATH, call_endpoint="serving_default")
    print(f"✅ Modelo Teachable Machine cargado correctamente desde: {MODEL_PATH}")
except Exception as e:
    print(f"❌ Error al cargar el modelo Teachable Machine:", e)
    model = None

# ======================================
# 🧠 Variables globales
# ======================================

CLASS_NAMES = ["Pencil", "Notebook", "Calculator"]
camera_active = False
camera_thread = None
last_frame = None
last_label = ""
last_confidence = 0.0
frame_lock = threading.Lock()
CONFIDENCE_THRESHOLD = 0.8  # 🔧 Ajustable (sube a 0.85 si aún hay falsos positivos)

# ======================================
# 🎥 Bucle de cámara
# ======================================

def tm_camera_loop():
    """
    Captura frames en tiempo real, realiza inferencia con el modelo TM,
    y actualiza las variables globales (frame, label, confidence).
    """
    global camera_active, last_frame, last_label, last_confidence

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ No se pudo acceder a la cámara.")
        return

    print("📷 Cámara iniciada para Teachable Machine.")

    while camera_active:
        ret, frame = cap.read()
        if not ret:
            continue

        h, w, _ = frame.shape
        x1, y1, x2, y2 = w // 4, h // 4, w * 3 // 4, h * 3 // 4
        roi = frame[y1:y2, x1:x2]

        label = "No reconocido"
        confidence = 0.0

        if model is not None:
            try:
                # === Preprocesamiento ===
                img_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
                img_resized = cv2.resize(img_rgb, (224, 224))
                img_norm = img_resized / 255.0
                x = tf.convert_to_tensor(img_norm, dtype=tf.float32)
                x = tf.expand_dims(x, axis=0)

                # === Inferencia ===
                y = model(x)
                if isinstance(y, dict):
                    y = list(y.values())[0]
                output = y.numpy()[0]

                pred_index = int(np.argmax(output))
                pred_label = CLASS_NAMES[pred_index]
                confidence = float(output[pred_index])

                # === Nueva lógica: marcar “no reconocido” si la confianza es baja ===
                if confidence < CONFIDENCE_THRESHOLD:
                    label = "No reconocido"
                    color = (0, 0, 255)  # 🔴 rojo (desconocido)
                else:
                    label = pred_label
                    color = (0, 255, 0)  # 🟢 verde (válido)

                # === Dibujar recuadro y texto ===
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    frame,
                    f"{label} ({confidence:.2f})",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    color,
                    2,
                )

                # === Guardar resultados globales ===
                with frame_lock:
                    last_frame = frame.copy()
                    last_label = label
                    last_confidence = confidence

            except Exception as e:
                print("❌ Error en predicción TM:", e)

        time.sleep(0.1)

    cap.release()
    print("🛑 Cámara TM detenida.")

# ======================================
# 🚀 Control del hilo
# ======================================

def start_tm_camera():
    global camera_active, camera_thread
    if not camera_active:
        camera_active = True
        camera_thread = threading.Thread(target=tm_camera_loop, daemon=True)
        camera_thread.start()
        print("🚀 Cámara TM iniciada en hilo separado.")

def stop_tm_camera():
    global camera_active
    camera_active = False
    print("🛑 Cámara TM detenida por solicitud.")

# ======================================
# 🖼️ Obtener frame actual
# ======================================

def get_tm_base64_frame():
    """
    Devuelve tanto el frame completo como el recorte (ROI)
    codificados en base64, junto con la etiqueta y confianza.
    """
    global last_frame, last_label, last_confidence

    if last_frame is None:
        return None

    h, w, _ = last_frame.shape
    x1, y1, x2, y2 = w // 4, h // 4, w * 3 // 4, h * 3 // 4
    roi = last_frame[y1:y2, x1:x2]

    _, buffer_full = cv2.imencode(".jpg", last_frame)
    frame_base64_full = base64.b64encode(buffer_full).decode("utf-8")

    _, buffer_roi = cv2.imencode(".jpg", roi)
    frame_base64_roi = base64.b64encode(buffer_roi).decode("utf-8")

    return {
        "frame": f"data:image/jpeg;base64,{frame_base64_full}",
        "roi": f"data:image/jpeg;base64,{frame_base64_roi}",
        "label": last_label or "none",
        "confidence": last_confidence or 0.0,
    }
