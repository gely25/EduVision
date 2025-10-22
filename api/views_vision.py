from django.shortcuts import render
from django.http import JsonResponse
from src.infrastructure.camera.tm_camera_service import (
    start_tm_camera,
    stop_tm_camera,
    get_tm_base64_frame,
)





import cv2, base64, threading
import numpy as np
from django.http import JsonResponse, HttpResponse
from keras.layers import TFSMLayer
import tensorflow as tf

camera_tm = None
thread_tm = None
last_frame = None
last_label = ""
last_confidence = 0.0
model_tm = None
running_tm = False






# 🌐 Página HTML del clasificador
def tm_live_view(request):
    return render(request, "recognition/tm_live.html")

# 🚀 Iniciar cámara
def start_tm_camera_view(request):
    start_tm_camera()
    return JsonResponse({"status": "Camera started"})

# 🛑 Detener cámara
def stop_tm_camera_view(request):
    stop_tm_camera()
    return JsonResponse({"status": "Camera stopped"})

# 📸 Obtener frame actual
import time

def tm_frame_view(request):
    """Devuelve el último frame del clasificador TM (base64 + predicción)."""
    from src.infrastructure.camera.tm_camera_service import get_tm_base64_frame

    # 🔁 Espera breve si el hilo aún no tiene frames
    max_wait = 3  # segundos
    start = time.time()

    while time.time() - start < max_wait:
        frame_data = get_tm_base64_frame()
        if frame_data:
            return JsonResponse(frame_data)
        time.sleep(0.1)

    print("⚠️ No hay frame disponible (probablemente la cámara no ha generado imagen todavía).")
    return JsonResponse({"error": "No frame available"}, status=404)
