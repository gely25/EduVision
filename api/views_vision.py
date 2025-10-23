from django.shortcuts import render
from django.http import JsonResponse
from src.infrastructure.camera.tm_camera_service import (
    start_tm_camera,
    stop_tm_camera,
    get_tm_base64_frame,
)
import time

# ======================================================
# 🌐 Página principal del clasificador TM
# ======================================================
def tm_live_view(request):
    """Renderiza la página del clasificador Teachable Machine."""
    return render(request, "recognition/tm_live.html")

# ======================================================
# 🚀 Iniciar cámara
# ======================================================
def start_tm_camera_view(request):
    """Inicia la cámara TM en un hilo separado."""
    try:
        start_tm_camera()
        print("✅ Cámara TM iniciada desde vista Django.")
        return JsonResponse({"status": "Camera started"})
    except Exception as e:
        print("❌ Error iniciando cámara TM:", e)
        return JsonResponse({"error": str(e)}, status=500)

# ======================================================
# 🛑 Detener cámara
# ======================================================
def stop_tm_camera_view(request):
    """Detiene la cámara y limpia datos de última detección."""
    try:
        stop_tm_camera()
        print("🛑 Cámara TM detenida desde vista Django.")
        return JsonResponse({"status": "Camera stopped"})
    except Exception as e:
        print("❌ Error al detener cámara TM:", e)
        return JsonResponse({"error": str(e)}, status=500)

# ======================================================
# 📸 Obtener frame actual
# ======================================================
def tm_frame_view(request):
    """
    Devuelve el último frame procesado por el clasificador TM.
    Incluye el frame codificado en base64, la predicción y confianza.
    """
    max_wait = 3
    start = time.time()

    while time.time() - start < max_wait:
        frame_data = get_tm_base64_frame()
        if frame_data:
            label = frame_data.get("label", "").strip().lower()
            confidence = float(frame_data.get("confidence", 0.0))
            base64_img = frame_data.get("image") or frame_data.get("frame")

            # Normalizamos salida
            if confidence < 0.6 or label in ["", "none", "unknown", "no reconocido"]:
                label = "No reconocido"
                confidence = 0.0

            # 🔹 Esta es la clave importante que tu front espera
            return JsonResponse({
                "frame": base64_img,
                "label": label,
                "confidence": confidence
            })

        time.sleep(0.1)

    print("⚠️ No hay frame disponible (probablemente la cámara aún no inició o se detuvo).")
    return JsonResponse({"error": "No frame available"}, status=404)
