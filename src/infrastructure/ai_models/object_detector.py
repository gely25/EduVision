import threading
import cv2
import base64
import numpy as np
from ultralytics import YOLO

import os
from ultralytics import YOLO


import os
from ultralytics import YOLO

# --- Buscar modelo YOLO en rutas posibles ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Carpetas donde puede estar el modelo
model_dirs = [
    os.path.join(BASE_DIR, "runs", "detect", "train_v2", "weights"),
    os.path.join(BASE_DIR, "runs", "detect", "train", "weights"),
]

# Buscar cualquier archivo .pt dentro de esas carpetas
model_path = None
for folder in model_dirs:
    if os.path.exists(folder):
        for file in os.listdir(folder):
            if file.endswith(".pt"):  # Acepta best.pt, best(1).pt, last.pt, etc.
                model_path = os.path.join(folder, file)
                break
    if model_path:
        break

if not model_path:
    raise FileNotFoundError(
        f"❌ No se encontró ningún archivo .pt en:\n" +
        "\n".join(model_dirs)
    )

# --- Cargar modelo YOLO ---
print(f"✅ Modelo detectado y cargado desde: {model_path}")
model = YOLO(model_path)

print("📋 Clases detectables:")
for i, name in model.names.items():
    print(f"   {i}: {name}")



# ✅ Variables globales compartidas
frame_lock = threading.Lock()
last_frame = None           # frame anotado
last_raw_frame = None       # frame original
last_boxes = []             # [(label, x1, y1, x2, y2)]
last_labels = []            # etiquetas detectadas


def detect_objects(frame):
    """Detecta objetos en un frame y actualiza variables globales."""
    global last_frame, last_raw_frame, last_boxes, last_labels

    if frame is None or frame.size == 0:
        print("⚠️ Frame vacío, se omite detección.")
        return [], []

    results = model(frame, conf=0.15, iou=0.4, verbose=False)
    
    # 🔍 Depuración temporal
    for r in results:
        if r.boxes is not None and len(r.boxes) > 0:
            print(f"🧠 Detectadas {len(r.boxes)} cajas:")
            for box in r.boxes:
                print(f"   → {model.names[int(box.cls[0])]} ({float(box.conf[0]):.2f})")
        else:
            print("⚠️ No se detectaron objetos en este frame.")

    labels, boxes = [], []

    annotated = frame.copy()
    last_raw_frame = frame.copy()

    for r in results:
        if not hasattr(r, "boxes") or r.boxes is None:
            continue

        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names.get(cls_id, "unknown")
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            labels.append(label)
            boxes.append((label, x1, y1, x2, y2))

            # Dibuja caja
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                annotated,
                f"{label} {conf:.2f}",
                (x1, max(20, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

    with frame_lock:
        last_frame = annotated.copy()
        last_raw_frame = frame.copy()
        last_boxes = boxes
        last_labels = list(set(labels))

    return labels, boxes


def get_detected_objects_with_images():
    """Devuelve las detecciones actuales con miniaturas base64."""
    global last_raw_frame, last_boxes
    objects_data = []

    with frame_lock:
        if last_raw_frame is None or not last_boxes:
            return []

        seen = set()
        h, w, _ = last_raw_frame.shape

        for label, x1, y1, x2, y2 in last_boxes:
            if label in seen:
                continue
            seen.add(label)

            # Corrige límites del recorte
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            crop = last_raw_frame[y1:y2, x1:x2]
            if crop.size == 0:
                continue

            _, buffer = cv2.imencode(".jpg", crop)
            base64_img = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"

            objects_data.append({
                "label": label,
                "bbox": [x1, y1, x2, y2],
                "image": base64_img
            })

    return objects_data


def get_cropped_object_by_label(label):
    """Devuelve la imagen base64 del objeto indicado."""
    global last_raw_frame, last_boxes
    with frame_lock:
        if last_raw_frame is None or not last_boxes:
            return None

        for lbl, x1, y1, x2, y2 in last_boxes:
            if lbl == label:
                h, w, _ = last_raw_frame.shape
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                crop = last_raw_frame[y1:y2, x1:x2]
                if crop.size == 0:
                    return None
                _, buffer = cv2.imencode(".jpg", crop)
                return f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"
    return None
















# import threading
# import time
# import cv2
# import base64
# import numpy as np
# from ultralytics import YOLO

# # ✅ Cargar modelo YOLOv8 una sola vez
# model = YOLO("yolov8n.pt")

# # ✅ Variables globales compartidas
# last_labels = []
# last_boxes = []
# last_frame = None
# frame_lock = threading.Lock()


# last_raw_frame = None  # nuevo: frame sin dibujos


# def detect_objects(frame):
#     """Detecta objetos en un frame, dibuja cajas y actualiza las variables globales."""
#     global last_labels, last_boxes, last_frame, last_raw_frame

#     results = model(frame)
#     labels, boxes = [], []

#     # ✅ Guarda el frame original antes de dibujar (para recortes)
#     last_raw_frame = frame.copy()
#     annotated_frame = frame.copy()

#     for r in results:
#         for box in r.boxes:
#             cls_id = int(box.cls[0])
#             label = model.names[cls_id]
#             conf = float(box.conf[0])
#             x1, y1, x2, y2 = map(int, box.xyxy[0])

#             labels.append(label)
#             boxes.append((label, x1, y1, x2, y2))

#             # Dibuja la caja en una copia separada
#             color = (0, 255, 0)
#             cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
#             cv2.putText(
#                 annotated_frame,
#                 f"{label} {conf:.2f}",
#                 (x1, max(20, y1 - 10)),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.6,
#                 (255, 255, 255),
#                 2
#             )

#     # ✅ Guarda ambos: frame con anotaciones y frame limpio
#     with frame_lock:
#         last_labels = list(set(labels))
#         last_boxes = boxes
#         last_frame = annotated_frame.copy()

#     return labels, boxes



# def get_detected_objects_with_images():
#     """Devuelve etiquetas con bbox y recorte exacto del objeto."""
#     global last_raw_frame, last_boxes
#     labels_with_images = []

#     with frame_lock:
#         if last_raw_frame is not None and last_boxes:
#             seen = set()
#             h, w, _ = last_raw_frame.shape

#             for label, x1, y1, x2, y2 in last_boxes:
#                 if label in seen:
#                     continue
#                 seen.add(label)

#                 # Validar coordenadas dentro del frame
#                 x1, y1 = max(0, x1), max(0, y1)
#                 x2, y2 = min(w, x2), min(h, y2)

#                 obj_crop = last_raw_frame[y1:y2, x1:x2]
#                 if obj_crop.size == 0:
#                     continue

#                 # Convertir a base64
#                 _, buffer = cv2.imencode(".jpg", obj_crop)
#                 base64_image = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"

#                 labels_with_images.append({
#                     "label": label,
#                     "bbox": [x1, y1, x2, y2],
#                     "image": base64_image
#                 })

#     return labels_with_images



# def get_cropped_object_by_label(label):
#     """Devuelve el recorte base64 exacto del objeto indicado por su label."""
#     global last_raw_frame, last_boxes
#     with frame_lock:
#         if last_raw_frame is None or not last_boxes:
#             return None

#         for lbl, x1, y1, x2, y2 in last_boxes:
#             if lbl == label:
#                 h, w, _ = last_raw_frame.shape
#                 x1, y1 = max(0, x1), max(0, y1)
#                 x2, y2 = min(w, x2), min(h, y2)

#                 obj_crop = last_raw_frame[y1:y2, x1:x2]
#                 if obj_crop.size == 0:
#                     return None

#                 _, buffer = cv2.imencode(".jpg", obj_crop)
#                 return f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"

#     return None
