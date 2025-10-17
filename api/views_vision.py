from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from src.infrastructure.camera.camera_service import (
    start_camera,
    stop_camera,
    get_base64_frame,
)
from src.infrastructure.ai_models.object_detector import (
    get_detected_objects_with_images,
    model,
)
import os
import cv2
import numpy as np
import base64
from django.conf import settings


# 🔹 Página principal
def live_view(request):
    return render(request, "recognition/live.html")


# 🔹 Iniciar cámara
def start_camera_view(request):
    start_camera()
    print("🚀 Cámara iniciada desde vista Django.")
    return JsonResponse({"status": "Camera started"})


# 🔹 Detener cámara
def stop_camera_view(request):
    stop_camera()
    print("🛑 Cámara detenida desde vista Django.")
    return JsonResponse({"status": "Camera stopped"})


# 🔹 Obtener detecciones actuales
def objects_view(request):
    detections = get_detected_objects_with_images()
    if not detections:
        print("⚠️ No se detectaron objetos.")
    else:
        print(f"✅ {len(detections)} objetos detectados.")
    return JsonResponse({"labels": detections})


# 🔹 Obtener último frame (base64)
def get_frame_view(request):
    """Devuelve el último frame procesado en formato Base64."""
    frame_data = get_base64_frame()
    if frame_data:
        print("📸 Frame entregado correctamente.")
        return JsonResponse({"frame": frame_data})
    print("⚠️ No hay frame disponible aún.")
    return JsonResponse({"error": "No frame available"}, status=404)


# 🔹 Detección manual por imagen subida
class DetectView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        image_file = request.FILES.get("image")
        if not image_file:
            return Response({"error": "No image provided"}, status=400)

        np_img = np.frombuffer(image_file.read(), np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        save_path = os.path.join(settings.MEDIA_ROOT, image_file.name)
        with open(save_path, "wb") as f:
            f.write(np_img)

        results = model(frame)
        detections = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])

                obj_crop = frame[y1:y2, x1:x2]
                _, buffer = cv2.imencode(".jpg", obj_crop)
                base64_image = (
                    f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"
                )

                detections.append(
                    {
                        "label": label,
                        "confidence": conf,
                        "bbox": [x1, y1, x2, y2],
                        "image": base64_image,
                    }
                )

        print(f"🔍 {len(detections)} detecciones procesadas manualmente.")
        return Response({"detections": detections})



# Agregar esto a tu views.py

def objects_view(request):
    """Endpoint compatible con el frontend"""
    detections = get_detected_objects_with_images()
    if not detections:
        print("⚠️ No se detectaron objetos.")
        return JsonResponse({"objects": []})
    else:
        print(f"✅ {len(detections)} objetos detectados.")
    return JsonResponse({"objects": detections})


def frame_view(request):
    """Devuelve el frame en base64"""
    frame_data = get_base64_frame()
    if frame_data:
        print("📸 Frame entregado correctamente.")
        return JsonResponse({"frame": frame_data})
    print("⚠️ No hay frame disponible aún.")
    return JsonResponse({"error": "No frame available"}, status=404)