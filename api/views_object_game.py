from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from src.infrastructure.orm.flashcards.models import Flashcard
from src.infrastructure.camera.tm_camera_service import get_tm_base64_frame
import random
import time


# ======================================================
# 🎬 Vistas iniciales del flujo educativo del juego
# ======================================================

def intro_view(request):
    return render(request, 'object_game/intro.html')

def instructions_view(request):
    return render(request, 'object_game/instructions.html')

def rules_view(request):
    return render(request, 'object_game/rules.html')

def camera_test_view(request):
    return render(request, 'object_game/camera_test.html')


# ======================================================
# 🎮 Inicio del juego — valida progreso antes de permitir jugar
# ======================================================
@login_required
def start_view(request):
    """
    Verifica si el usuario tiene al menos 5 flashcards dominadas.
    Si no cumple, muestra un mensaje para seguir estudiando.
    Si cumple, selecciona 5 palabras y prepara la sesión de juego.
    """

    # 🔹 Obtiene las flashcards dominadas por el usuario actual
    mastered = Flashcard.objects.filter(user=request.user, is_mastered=True)

    if mastered.count() < 5:
        # 🔸 Muestra plantilla de advertencia
        return render(request, "object_game/insufficient_flashcards.html", {
            "faltan": 5 - mastered.count()
        })

    # 🔹 Selecciona 5 palabras aleatorias del vocabulario dominado
    palabras = random.sample(
        list(mastered.values_list("word", flat=True)),
        min(5, mastered.count())
    )

    # 🔹 Guarda la sesión
    request.session["palabras_juego"] = palabras
    request.session["puntaje"] = 0

    # 🔹 Redirige a la vista principal del juego
    return redirect("/api/object_game/play/")


# ======================================================
# 🕹️ Pantalla principal del juego
# ======================================================
@login_required
def play_view(request):
    """
    Renderiza la página principal del juego:
    - Carga las palabras guardadas en sesión.
    - Si no hay sesión válida, redirige al inicio.
    """
    palabras = request.session.get("palabras_juego", [])
    if not palabras:
        return redirect("/api/object_game/start/")

    return render(request, "object_game/play.html", {"palabras": palabras})


# ======================================================
# 📸 Detección del objeto mostrado con TM
# ======================================================
@login_required
def detectar_objeto(request):
    """
    Obtiene el frame actual y la etiqueta detectada desde el servicio TM.
    Devuelve JSON con el label y nivel de confianza.
    """
    data = get_tm_base64_frame()
    if not data:
        return JsonResponse({"label": "No reconocido"})

    label = data.get("label", "No reconocido")
    conf = data.get("confidence", 0.0)

    # 🔹 Filtro de confianza mínima
    if conf < 0.6:
        label = "No reconocido"

    return JsonResponse({"label": label})


# ======================================================
# 🏁 Resultado final del juego
# ======================================================
@login_required
def result_view(request):
    """
    Muestra el resultado final del juego con puntaje.
    """
    puntaje = request.session.get("puntaje", 0)
    max_puntaje = 50

    return render(request, "object_game/result.html", {
        "puntaje": puntaje,
        "max_puntaje": max_puntaje
    })
