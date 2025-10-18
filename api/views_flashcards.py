from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from src.infrastructure.orm.flashcards.models import Flashcard

from django.utils import timezone
import json
import base64
from django.core.files.base import ContentFile

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from src.infrastructure.orm.flashcards.models import Flashcard
from deep_translator import GoogleTranslator
import json, base64











from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from src.infrastructure.orm.flashcards.models import Flashcard
from src.infrastructure.ai_models.object_detector import get_cropped_object_by_label
from deep_translator import GoogleTranslator
from django.utils import timezone
from django.core.files.base import ContentFile
from PIL import Image
import json, base64, io

# ------------------------------------------------------
# 🧩 Añadir nueva flashcard automáticamente desde YOLO
# ------------------------------------------------------
@csrf_exempt
def add_flashcard(request):
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

    if not traduccion or traduccion == "Traducción pendiente":
        try:
            traduccion = GoogleTranslator(source="en", target="es").translate(palabra)
        except Exception as e:
            traduccion = "Error al traducir"
            print("❌ Error traduciendo:", e)

    if Flashcard.objects.filter(palabra=palabra).exists():
        return JsonResponse({"error": "Flashcard ya existe"}, status=400)

    base64_crop = get_cropped_object_by_label(palabra)
    if not base64_crop:
        print(f"⚠️ No se encontró el recorte para '{palabra}'")
        return JsonResponse({"error": "No se encontró el objeto en el frame actual"}, status=404)

    flashcard = Flashcard(palabra=palabra, traduccion=traduccion)

    try:
        img_data = base64_crop.split(",")[1] if "," in base64_crop else base64_crop
        image_bytes = base64.b64decode(img_data)
        image = Image.open(io.BytesIO(image_bytes))
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        flashcard.imagen.save(f"{palabra}.png", ContentFile(buffer.getvalue()), save=True)
        print(f"✅ Imagen recortada y guardada correctamente para '{palabra}'")
    except Exception as e:
        print("❌ Error guardando imagen:", e)
        return JsonResponse({"error": f"Error guardando la imagen: {str(e)}"}, status=500)

    flashcard.save()
    print(f"✅ Flashcard guardada: {flashcard.palabra} ({flashcard.traduccion})")

    return JsonResponse({
        "id": flashcard.id,
        "palabra": flashcard.palabra,
        "traduccion": flashcard.traduccion,
        "imagen": flashcard.imagen.url if flashcard.imagen else ""
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
# 🔁 Obtener solo las flashcards que deben revisarse hoy
# ------------------------------------------------------


# ------------------------------------------------------
# 🧠 Nueva vista: marcar como Recordado u Olvidado
# ------------------------------------------------------
# @csrf_exempt
# def mark_flashcard(request, id):
#     """
#     Marca una flashcard como recordada u olvidada.
#     - success=True  → duplicar el intervalo y programar revisión más adelante.
#     - success=False → reiniciar intervalo para repasarla pronto.
#     """
#     if request.method != "POST":
#         return JsonResponse({"error": "Método no permitido"}, status=405)

#     try:
#         data = json.loads(request.body.decode("utf-8"))
#     except json.JSONDecodeError:
#         return JsonResponse({"error": "Cuerpo no es JSON válido"}, status=400)

#     success = data.get("success", True)
#     today = timezone.now().date()

#     try:
#         flashcard = Flashcard.objects.get(id=id)
#     except Flashcard.DoesNotExist:
#         return JsonResponse({"error": "Flashcard no encontrada"}, status=404)

#     # 🔁 Aplicar la lógica de repetición espaciada
#     if success:
#         flashcard.interval *= 2  # recordado → más espacio
#     else:
#         flashcard.interval = 1   # olvidado → repaso inmediato

#     flashcard.next_review = today + timezone.timedelta(days=flashcard.interval)
#     flashcard.save()

#     return JsonResponse({
#         "id": flashcard.id,
#         "palabra": flashcard.palabra,
#         "traduccion": flashcard.traduccion,
#         "interval": flashcard.interval,
#         "next_review": flashcard.next_review.isoformat(),
#         "success": success
#     })




# from django.shortcuts import render

# def review_page(request):
#     """Renderiza la página HTML del repaso de flashcards."""
#     return render(request, "flashcards/review.html")








from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.utils import timezone
from src.infrastructure.orm.flashcards.models import Flashcard
import json

# --------- PÁGINAS ---------

def flashcards_page(request):
    """Dashboard principal de Flashcards (vista tipo Figma)."""
    return render(request, "flashcards/index.html")

def flashcards_review_page(request):
    """Página de repaso (la de voltear tarjeta). Si tu template se llama distinto, cámbialo aquí."""
    return render(request, "flashcards/review.html")


# --------- API: RESUMEN / LISTAS ---------

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
    """
    Devuelve:
      - counters: pending, mastered, total
      - pending:   tarjetas con next_review <= hoy (toca estudiar)
      - mastered:  tarjetas con next_review  > hoy (dominadas por ahora)
    """
    today = timezone.now().date()
    pending_qs  = Flashcard.objects.filter(next_review__lte=today).order_by("next_review", "palabra")
    mastered_qs = Flashcard.objects.filter(next_review__gt=today).order_by("palabra")

    data = {
        "counters": {
            "pending": pending_qs.count(),
            "mastered": mastered_qs.count(),
            "total": Flashcard.objects.count(),
        },
        "pending":  [_serialize_card(f) for f in pending_qs],
        "mastered": [_serialize_card(f) for f in mastered_qs],
    }
    return JsonResponse(data)


# --------- API: MARCAR RECORDADO / OLVIDADO ---------

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
















from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, Http404
from django.utils import timezone
import json
from src.infrastructure.orm.flashcards.models import Flashcard

@csrf_exempt
def mark_flashcard(request, id: int):
    """
    POST { "success": true|false }
      true  -> recordado: duplica el intervalo y programa la próxima revisión más adelante.
      false -> olvidado : reinicia el intervalo y vuelve a estado pendiente.
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

    # ✅ Lógica de repetición espaciada
    today = timezone.now().date()
    if success:
        f.interval = max(1, f.interval * 2)
    else:
        f.interval = 1
    f.next_review = today + timezone.timedelta(days=f.interval)
    f.save()

    print(f"✅ Flashcard '{f.palabra}' marcada como {'recordada' if success else 'olvidada'}")

    # Devuelve nuevo resumen actualizado
    from django.http import JsonResponse
    return JsonResponse({
        "id": f.id,
        "palabra": f.palabra,
        "traduccion": f.traduccion,
        "interval": f.interval,
        "next_review": f.next_review.isoformat(),
        "success": success
    })
