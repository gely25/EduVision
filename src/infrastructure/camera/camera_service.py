import cv2, base64, threading, numpy as np
from keras.layers import TFSMLayer

camera_tm = None
thread_tm = None
running_tm = False
last_frame = None
last_label = ""
last_confidence = 0.0
model_tm = None


# 🚀 Iniciar cámara TM
def start_tm_camera():
    global camera_tm, thread_tm, running_tm, model_tm

    if running_tm:
        print("⚠️ Cámara TM ya está en ejecución.")
        return

    print("🚀 Cámara TM iniciada en hilo separado.")
    model_tm = TFSMLayer("model.savedmodel", call_endpoint="serving_default")

    camera_tm = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    running_tm = True

    thread_tm = threading.Thread(target=_tm_camera_loop, daemon=True)
    thread_tm.start()


# 🛑 Detener cámara TM
def stop_tm_camera():
    global running_tm, camera_tm
    running_tm = False
    if camera_tm is not None:
        camera_tm.release()
        camera_tm = None
    print("🛑 Cámara TM detenida por solicitud.")


# 🔁 Bucle de lectura y clasificación
def _tm_camera_loop():
    global camera_tm, running_tm, last_frame, last_label, last_confidence, model_tm

    labels = ["pencil", "notebook", "calculator"]
    print("📷 Cámara iniciada para Teachable Machine.")

    while running_tm:
        ret, frame = camera_tm.read()
        if not ret:
            continue

        img = cv2.resize(frame, (224, 224))
        img = np.expand_dims(img / 255.0, axis=0)

        preds = model_tm(img)
        output = preds["output_0"] if isinstance(preds, dict) else preds
        idx = np.argmax(output)
        conf = float(np.max(output))

        last_label = labels[idx]
        last_confidence = conf
        last_frame = frame


# 🎥 Devolver frame codificado
def get_tm_base64_frame():
    global last_frame, last_label, last_confidence

    if last_frame is None:
        return None

    # Codificar el frame a base64
    _, buffer = cv2.imencode(".jpg", last_frame)
    frame_base64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "frame": f"data:image/jpeg;base64,{frame_base64}",
        "label": last_label,
        "confidence": last_confidence,
    }
