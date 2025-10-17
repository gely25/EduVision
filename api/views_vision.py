from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
import cv2
import numpy as np
import base64

# 🔹 Servicios e infraestructura
from src.infrastructure.camera.camera_service import (
    start_camera,
    stop_camera,
    get_base64_frame,
)
from src.infrastructure.ai_models.object_detector import (
    get_detected_objects_with_images,
    model,
)


# 🧠 Página principal de reconocimiento
def live_view(request):
    """Renderiza la vista principal con la cámara."""
    return render(request, "recognition/live.html")


# 🚀 Iniciar cámara
def start_camera_view(request):
    """Inicia el flujo de video y detección."""
    start_camera()
    print("🚀 Cámara iniciada desde Django.")
    return JsonResponse({"status": "Camera started"})


# 🛑 Detener cámara
def stop_camera_view(request):
    """Detiene el flujo de video y libera recursos."""
    stop_camera()
    print("🛑 Cámara detenida desde Django.")
    return JsonResponse({"status": "Camera stopped"})


# 📸 Obtener frame actual (base64)
def get_frame_view(request):
    """Devuelve el último frame (ya procesado) como imagen base64."""
    frame_data = get_base64_frame()
    if frame_data:
        return JsonResponse({"frame": frame_data})
    return JsonResponse({"error": "No frame available"}, status=404)


# 🔍 Obtener objetos detectados en vivo (YOLOv8)
def objects_view(request):
    """
    Devuelve los objetos detectados en el último frame, con:
    - label
    - bbox [x1, y1, x2, y2]
    - imagen recortada base64
    """
    detections = get_detected_objects_with_images()

    if not detections:
        print("⚠️ No se detectaron objetos.")
        return JsonResponse({"objects": []})

    print(f"✅ {len(detections)} objetos detectados: {[d['label'] for d in detections]}")
    return JsonResponse({"objects": detections})


# 📂 Detección manual (para pruebas POST con imagen)
class DetectView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        """Permite probar detección subiendo una imagen manualmente."""
        image_file = request.FILES.get("image")
        if not image_file:
            return Response({"error": "No image provided"}, status=400)

        # Leer imagen subida
        np_img = np.frombuffer(image_file.read(), np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        results = model(frame)
        detections = []

        for r in results:
            if not hasattr(r, "boxes") or r.boxes is None:
                continue

            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names.get(cls_id, "unknown")
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                obj_crop = frame[y1:y2, x1:x2]
                if obj_crop.size == 0:
                    continue

                _, buffer = cv2.imencode(".jpg", obj_crop)
                base64_image = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"

                detections.append({
                    "label": label,
                    "confidence": round(conf, 2),
                    "bbox": [x1, y1, x2, y2],
                    "image": base64_image,
                })

        print(f"🔍 {len(detections)} detecciones procesadas manualmente.")
        return Response({"detections": detections})












# from django.http import JsonResponse
# from django.shortcuts import render
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.parsers import MultiPartParser
# from django.conf import settings
# import os
# import cv2
# import numpy as np
# import base64

# # 🔹 Importaciones del dominio e infraestructura
# from src.infrastructure.camera.camera_service import (
#     start_camera,
#     stop_camera,
#     get_base64_frame,
# )
# from src.infrastructure.ai_models.object_detector import (
#     get_detected_objects_with_images,
#     model,
# )


# # 🧠 Página principal de reconocimiento
# def live_view(request):
#     """Renderiza la página principal con el streaming de cámara."""
#     return render(request, "recognition/live.html")


# # 🚀 Iniciar cámara
# def start_camera_view(request):
#     start_camera()
#     print("🚀 Cámara iniciada desde vista Django.")
#     return JsonResponse({"status": "Camera started"})


# # 🛑 Detener cámara
# def stop_camera_view(request):
#     stop_camera()
#     print("🛑 Cámara detenida desde vista Django.")
#     return JsonResponse({"status": "Camera stopped"})


# # 📸 Obtener frame actual (base64)
# def get_frame_view(request):
#     """Devuelve el último frame procesado en formato Base64 para el frontend."""
#     frame_data = get_base64_frame()
#     if frame_data:
#         print("📸 Frame entregado correctamente.")
#         return JsonResponse({"frame": frame_data})
#     print("⚠️ No hay frame disponible aún.")
#     return JsonResponse({"error": "No frame available"}, status=404)


# # 🔍 Obtener detecciones actuales (YOLOv8)
# def objects_view(request):
#     """
#     Devuelve la lista de objetos detectados en el último frame con:
#     - etiqueta (label)
#     - coordenadas bbox [x1, y1, x2, y2]
#     - recorte del objeto en base64
#     """
#     detections = get_detected_objects_with_images()
#     if not detections:
#         print("⚠️ No se detectaron objetos.")
#         return JsonResponse({"objects": []})

#     print(f"✅ {len(detections)} objetos detectados.")
#     return JsonResponse({"objects": detections})


# # 📂 Detección manual por imagen subida (para pruebas)
# class DetectView(APIView):
#     parser_classes = [MultiPartParser]

#     def post(self, request, format=None):
#         """Permite probar detección subiendo una imagen manualmente."""
#         image_file = request.FILES.get("image")
#         if not image_file:
#             return Response({"error": "No image provided"}, status=400)

#         # Convertir imagen en array de OpenCV
#         np_img = np.frombuffer(image_file.read(), np.uint8)
#         frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

#         results = model(frame)
#         detections = []

#         for r in results:
#             for box in r.boxes:
#                 cls_id = int(box.cls[0])
#                 label = model.names[cls_id]
#                 x1, y1, x2, y2 = map(int, box.xyxy[0])
#                 conf = float(box.conf[0])

#                 # Recorte del objeto
#                 obj_crop = frame[y1:y2, x1:x2]
#                 if obj_crop.size == 0:
#                     continue

#                 _, buffer = cv2.imencode(".jpg", obj_crop)
#                 base64_image = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"

#                 detections.append({
#                     "label": label,
#                     "confidence": conf,
#                     "bbox": [x1, y1, x2, y2],
#                     "image": base64_image,
#                 })

#         print(f"🔍 {len(detections)} detecciones procesadas manualmente.")
#         return Response({"detections": detections})
