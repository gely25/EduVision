from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.shortcuts import render
from deep_translator import GoogleTranslator
from src.infrastructure.orm.flashcards.models import Flashcard
from src.infrastructure.camera.tm_camera_service import get_tm_base64_frame  # ✅ usamos TM

from PIL import Image
from django.core.files.base import ContentFile
import json, base64, io


# ------------------------------------------------------
# 🧩 Añadir nueva flashcard (solo recorte del cuadro TM)
from django.db import IntegrityError

@csrf_exempt
def add_flashcard(request):
    """
    Crea una nueva flashcard a partir del objeto reconocido actualmente por el modelo TM.
    - Usa solo el área del recuadro central (ROI) como imagen base.
    - Traduce automáticamente el nombre del objeto.
    - Ignora casos en que el modelo devuelva "No reconocido" o similar.
    - Asocia la flashcard al usuario logueado (si lo hay).
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Cuerpo no es JSON válido"}, status=400)

    palabra = data.get("palabra")
    traduccion = data.get("traduccion")

    if not palabra:
        return JsonResponse({"error": "Falta palabra"}, status=400)

    # 🚫 Evitar crear flashcards si el objeto no fue reconocido
    if palabra.lower() in ["no reconocido", "none", "unknown"]:
        return JsonResponse({"error": "Objeto no reconocido, no se puede crear flashcard."}, status=400)

    # 🌍 Traducción automática (si no se envía)
    if not traduccion or traduccion == "Traducción pendiente":
        try:
            traduccion = GoogleTranslator(source="en", target="es").translate(palabra)
        except Exception:
            traduccion = "Error al traducir"

    # 📸 Obtener frame actual desde la cámara TM
    frame_data = get_tm_base64_frame()
    if not frame_data or "roi" not in frame_data:
        return JsonResponse({"error": "No hay frame disponible"}, status=404)

    base64_frame = frame_data["roi"]

    # 🆕 Crear instancia de flashcard (aún no guardada)
    flashcard = Flashcard(palabra=palabra, traduccion=traduccion)
    if request.user.is_authenticated:
        flashcard.user = request.user

    try:
        # 🖼️ Guardar imagen
        img_data = base64_frame.split(",")[1] if "," in base64_frame else base64_frame
        image_bytes = base64.b64decode(img_data)
        image = Image.open(io.BytesIO(image_bytes))
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        flashcard.imagen.save(f"{palabra}.png", ContentFile(buffer.getvalue()), save=False)

        # 💾 Intentar guardar en base de datos
        flashcard.save()
        print(f"✅ Flashcard guardada: {palabra} ({traduccion})")

    except IntegrityError:
        # ⚠️ Si se intenta insertar un duplicado (violación UNIQUE)
        return JsonResponse({
            "error": f"La palabra '{palabra}' ya fue agregada previamente."
        }, status=400)

    except Exception as e:
        print("❌ Error guardando flashcard:", e)
        return JsonResponse({"error": f"Ocurrió un error al guardar: {str(e)}"}, status=500)

    return JsonResponse({
        "id": flashcard.id,
        "palabra": flashcard.palabra,
        "traduccion": flashcard.traduccion,
        "imagen": flashcard.imagen.url if flashcard.imagen else "",
        "usuario": flashcard.user.username if flashcard.user else None
    })

# ------------------------------------------------------
# 📋 Listar todas las flashcards existentes
# ------------------------------------------------------
def flashcards_list(request):
    flashcards = Flashcard.objects.all()
    data = [
        {
            "id": f.id,
            "palabra": f.palabra,
            "traduccion": f.traduccion,
            "imagen": f.imagen.url if f.imagen else "",
            "next_review": f.next_review,
            "interval": f.interval,
        }
        for f in flashcards
    ]
    return JsonResponse(data, safe=False)


# ------------------------------------------------------
# 🧠 Páginas HTML
# ------------------------------------------------------
def flashcards_page(request):
    """Dashboard principal de Flashcards."""
    return render(request, "flashcards/index.html")

def flashcards_review_page(request):
    """Página de repaso (voltear tarjetas)."""
    return render(request, "flashcards/review.html")


# ------------------------------------------------------
# 📊 Resumen general y revisión
# ------------------------------------------------------
def _serialize_card(f: Flashcard):
    return {
        "id": f.id,
        "palabra": f.palabra,
        "traduccion": f.traduccion,
        "imagen": f.imagen.url if f.imagen else "",
        "next_review": f.next_review.isoformat() if f.next_review else None,
        "interval": f.interval,
    }

def flashcards_summary(request):
    """Devuelve counters y tarjetas pendientes / dominadas del usuario actual."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Usuario no autenticado"}, status=401)

    today = timezone.now().date()
    user = request.user

    # 🔹 Solo flashcards del usuario
    user_cards = Flashcard.objects.filter(user=user)

    # 🔸 Pendientes y Dominadas basadas en next_review
    pending_qs = user_cards.filter(next_review__lte=today).order_by("next_review", "palabra")
    mastered_qs = user_cards.filter(next_review__gt=today).order_by("palabra")

    data = {
        "counters": {
            "pending": pending_qs.count(),
            "mastered": mastered_qs.count(),
            "total": user_cards.count(),
        },
        "pending":  [_serialize_card(f) for f in pending_qs],
        "mastered": [_serialize_card(f) for f in mastered_qs],
    }
    return JsonResponse(data)



def review_flashcards(request):
    """Devuelve solo las flashcards que deben repasarse hoy."""
    today = timezone.now().date()
    flashcards = Flashcard.objects.filter(next_review__lte=today).order_by("palabra")
    data = [
        {
            "id": f.id,
            "palabra": f.palabra,
            "traduccion": f.traduccion,
            "imagen": f.imagen.url if f.imagen else "",
        }
        for f in flashcards
    ]
    return JsonResponse(data, safe=False)


# ------------------------------------------------------
# 🔁 Marcar como Recordado u Olvidado
# ------------------------------------------------------
@csrf_exempt
def mark_flashcard(request, id: int):
    """
    POST { "success": true|false }
    - true: recordado → duplica el intervalo.
    - false: olvidado → reinicia intervalo a 1.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
        success = bool(body.get("success"))
    except Exception as e:
        print("❌ Error parseando JSON:", e)
        return JsonResponse({"error": "JSON inválido"}, status=400)

    try:
        f = Flashcard.objects.get(id=id)
    except Flashcard.DoesNotExist:
        raise Http404("Flashcard no encontrada")

    today = timezone.now().date()

    # 🔁 Repetición espaciada
    if success:
        f.interval = max(1, f.interval * 2)
        f.next_review = today + timezone.timedelta(days=f.interval)
        estado = "dominada"
    else:
        f.interval = 1
        f.next_review = today
        estado = "pendiente"

    f.save()
    print(f"🔁 Flashcard '{f.palabra}' marcada como {estado} (intervalo: {f.interval} día/s)")

    return flashcards_summary(request)
