import threading
import time
import cv2
import base64
import numpy as np
from ultralytics import YOLO

# ✅ Cargar modelo YOLOv8 una sola vez
model = YOLO("yolov8n.pt")

# ✅ Variables globales compartidas
last_labels = []
last_boxes = []
last_frame = None
frame_lock = threading.Lock()


def detect_objects(frame):
    """Detecta objetos en un frame, dibuja las cajas y actualiza las variables globales."""
    global last_labels, last_boxes, last_frame

    results = model(frame)
    labels, boxes = [], []
    annotated_frame = frame.copy()  # copia para dibujar

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            labels.append(label)
            boxes.append((label, x1, y1, x2, y2))

            # 🔹 Dibujar rectángulo y etiqueta sobre el frame
            color = (0, 255, 0)  # verde por defecto
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                annotated_frame,
                f"{label} {conf:.2f}",
                (x1, max(20, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

    # ✅ Guardar frame procesado (con cajas y texto)
    with frame_lock:
        last_labels = list(set(labels))
        last_boxes = boxes
        last_frame = annotated_frame.copy()

    return labels, boxes


def get_detected_objects_with_images():
    """Devuelve las etiquetas detectadas junto con sus recortes en base64."""
    global last_frame, last_boxes
    labels_with_images = []

    with frame_lock:
        if last_frame is not None and last_boxes:
            seen = set()
            for label, x1, y1, x2, y2 in last_boxes:
                if label in seen:
                    continue
                seen.add(label)

                obj_crop = last_frame[y1:y2, x1:x2]
                if obj_crop.size == 0:
                    continue

                _, buffer = cv2.imencode(".jpg", obj_crop)
                base64_image = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"
                labels_with_images.append({"label": label, "image": base64_image})

    return labels_with_images
