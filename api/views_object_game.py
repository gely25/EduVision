from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from src.infrastructure.orm.flashcards.models import Flashcard
from src.infrastructure.camera.tm_camera_service import get_tm_base64_frame
from src.infrastructure.orm.object_game.models import GameSession
import random


# ======================================================
# 🎬 Vistas iniciales de introducción y reglas
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
# 🎮 Inicio del juego
# ======================================================
@login_required
def start_view(request):
    """
    Verifica si el usuario tiene al menos 5 flashcards dominadas (next_review futura).
    Si no cumple, muestra un mensaje.
    Si cumple, selecciona 5 aleatorias y prepara la sesión.
    """
    today = timezone.now().date()
    mastered = Flashcard.objects.filter(
        user=request.user, next_review__gt=today
    )

    if mastered.count() < 5:
        return render(request, "object_game/insufficient_flashcards.html", {
            "faltan": 5 - mastered.count()
        })

    palabras = random.sample(
        list(mastered.values_list("palabra", flat=True)),
        min(5, mastered.count())
    )

    request.session["palabras_juego"] = palabras
    request.session["puntaje"] = 0

    return redirect("/api/object_game/play/")


# ======================================================
# 🕹️ Pantalla principal
# ======================================================
@login_required
def play_view(request):
    palabras = request.session.get("palabras_juego", [])
    if not palabras:
        return redirect("/api/object_game/start/")

    return render(request, "object_game/play.html", {"palabras": palabras})


# ======================================================
# 📸 Detección con TM
# ======================================================
@login_required
def detectar_objeto(request):
    data = get_tm_base64_frame()
    if not data:
        return JsonResponse({"label": "No reconocido"})

    label = data.get("label", "No reconocido")
    conf = data.get("confidence", 0.0)

    if conf < 0.6:
        label = "No reconocido"

    return JsonResponse({"label": label})


# ======================================================
# 🏁 Resultado final
# ======================================================
@login_required
def result_view(request):
    """Muestra y guarda resultado final."""
    puntaje = request.session.get("puntaje", 0)
    max_puntaje = 50
    total_palabras = len(request.session.get("palabras_juego", []))

    # 🔹 Guardar la sesión de juego
    GameSession.objects.create(
        user=request.user,
        score=puntaje,
        total_words=total_palabras
    )

    return render(request, "object_game/result.html", {
        "puntaje": puntaje,
        "max_puntaje": max_puntaje
    })





from django.views.decorators.csrf import csrf_exempt

# ======================================================
# 💾 Guardar puntaje dinámico durante la partida
# ======================================================
@csrf_exempt
@login_required
def update_score_view(request):
    """
    Recibe el puntaje actual desde el frontend y lo guarda en la sesión y DB temporal.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        new_score = int(data.get("score", 0))
    except Exception as e:
        return JsonResponse({"error": f"JSON inválido: {e}"}, status=400)

    # 🔹 Actualiza en sesión
    request.session["puntaje"] = new_score

    # 🔹 Guarda también una sesión temporal (último puntaje en DB)
    GameSession.objects.update_or_create(
        user=request.user,
        date_played__date=timezone.now().date(),
        defaults={"score": new_score, "total_words": len(request.session.get("palabras_juego", []))}
    )

    return JsonResponse({"status": "ok", "puntaje_guardado": new_score})






# from django.shortcuts import render, redirect
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from src.infrastructure.orm.flashcards.models import Flashcard
# from src.infrastructure.camera.tm_camera_service import get_tm_base64_frame
# import random
# import time

# from src.infrastructure.orm.object_game.models import GameSession
# # ======================================================
# # 🎬 Vistas iniciales del flujo educativo del juego
# # ======================================================

# def intro_view(request):
#     return render(request, 'object_game/intro.html')

# def instructions_view(request):
#     return render(request, 'object_game/instructions.html')

# def rules_view(request):
#     return render(request, 'object_game/rules.html')

# def camera_test_view(request):
#     return render(request, 'object_game/camera_test.html')


# # ======================================================
# # 🎮 Inicio del juego — valida progreso antes de permitir jugar
# # ======================================================
# @login_required
# def start_view(request):
#     """
#     Verifica si el usuario tiene al menos 5 flashcards dominadas
#     (según la lógica de next_review > hoy).
#     """
#     today = time.timezone.now().date()
#     mastered = Flashcard.objects.filter(next_review__gt=today)

#     if mastered.count() < 5:
#         return render(request, "object_game/insufficient_flashcards.html", {
#             "faltan": 5 - mastered.count()
#         })

#     palabras = random.sample(
#         list(mastered.values_list("palabra", flat=True)),
#         min(5, mastered.count())
#     )

#     request.session["palabras_juego"] = palabras
#     request.session["puntaje"] = 0

#     return redirect("/api/object_game/play/")

# # ======================================================
# # 🕹️ Pantalla principal del juego
# # ======================================================
# @login_required
# def play_view(request):
#     """
#     Renderiza la página principal del juego:
#     - Carga las palabras guardadas en sesión.
#     - Si no hay sesión válida, redirige al inicio.
#     """
#     palabras = request.session.get("palabras_juego", [])
#     if not palabras:
#         return redirect("/api/object_game/start/")

#     return render(request, "object_game/play.html", {"palabras": palabras})


# # ======================================================
# # 📸 Detección del objeto mostrado con TM
# # ======================================================
# @login_required
# def detectar_objeto(request):
#     """
#     Obtiene el frame actual y la etiqueta detectada desde el servicio TM.
#     Devuelve JSON con el label y nivel de confianza.
#     """
#     data = get_tm_base64_frame()
#     if not data:
#         return JsonResponse({"label": "No reconocido"})

#     label = data.get("label", "No reconocido")
#     conf = data.get("confidence", 0.0)

#     # 🔹 Filtro de confianza mínima
#     if conf < 0.6:
#         label = "No reconocido"

#     return JsonResponse({"label": label})


# # ======================================================
# # 🏁 Resultado final del juego
# # ======================================================
# @login_required



# @login_required
# def result_view(request):
#     """
#     Muestra el resultado final del juego y registra la partida.
#     """
#     puntaje = request.session.get("puntaje", 0)
#     palabras = request.session.get("palabras_juego", [])
#     total_palabras = len(palabras)

#     # 🔹 Guardar la sesión en la base de datos
#     GameSession.objects.create(
#         user=request.user,
#         score=puntaje,
#         total_words=total_palabras
#     )

#     # 🔹 Renderizar la plantilla de resultado
#     return render(request, "object_game/result.html", {
#         "puntaje": puntaje,
#         "max_puntaje": total_palabras * 10,
#         "total": total_palabras
#     })
