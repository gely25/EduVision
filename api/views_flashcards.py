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
from django.core.files.base import ContentFile
from src.infrastructure.orm.flashcards.models import Flashcard
from deep_translator import GoogleTranslator
from django.utils import timezone
from PIL import Image
import json, base64, io



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from src.infrastructure.orm.flashcards.models import Flashcard
from deep_translator import GoogleTranslator
from django.utils import timezone
from PIL import Image
import json, base64, io



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.utils import timezone
from deep_translator import GoogleTranslator
from PIL import Image
import json, base64, io

# 🔹 Modelos y detector
from src.infrastructure.orm.flashcards.models import Flashcard
from src.infrastructure.ai_models.object_detector import get_cropped_object_by_label


# ------------------------------------------------------
# 🧩 Añadir nueva flashcard automáticamente desde YOLO
# ------------------------------------------------------
@csrf_exempt
def add_flashcard(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    # 🧩 Leer datos enviados por el frontend
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Cuerpo no es JSON válido"}, status=400)

    palabra = data.get("palabra")
    traduccion = data.get("traduccion")

    if not palabra:
        return JsonResponse({"error": "Falta palabra"}, status=400)

    # 🧠 Traducir automáticamente si es necesario
    if not traduccion or traduccion == "Traducción pendiente":
        try:
            traduccion = GoogleTranslator(source="en", target="es").translate(palabra)
        except Exception as e:
            traduccion = "Error al traducir"
            print("❌ Error traduciendo:", e)

    # 🚫 Evitar duplicados
    if Flashcard.objects.filter(palabra=palabra).exists():
        return JsonResponse({"error": "Flashcard ya existe"}, status=400)

    # 🧩 Obtener el recorte exacto desde el backend (YOLO)
    base64_crop = get_cropped_object_by_label(palabra)
    if not base64_crop:
        print(f"⚠️ No se encontró el recorte para '{palabra}'")
        return JsonResponse({"error": "No se encontró el objeto en el frame actual"}, status=404)

    # 💾 Crear flashcard
    flashcard = Flashcard(palabra=palabra, traduccion=traduccion)

    try:
        # Convertir imagen base64 a archivo PNG
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
            "imagen": f.imagen.url if f.imagen else ""
        }
        for f in flashcards
    ]
    return JsonResponse(data, safe=False)


# ------------------------------------------------------
# 🔁 Obtener solo las flashcards que deben revisarse hoy
# ------------------------------------------------------
def review_flashcards(request):
    today = timezone.now().date()
    flashcards = Flashcard.objects.filter(next_review__lte=today)
    data = [
        {
            "id": f.id,
            "palabra": f.palabra,
            "traduccion": f.traduccion,
            "imagen": f.imagen.url if f.imagen else ""
        }
        for f in flashcards
    ]
    return JsonResponse(data, safe=False)

























# @csrf_exempt
# def add_flashcard(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Método no permitido"}, status=405)

#     # 🧩 Leer y validar datos del frontend
#     try:
#         data = json.loads(request.body.decode("utf-8"))
#     except json.JSONDecodeError:
#         return JsonResponse({"error": "Cuerpo no es JSON válido"}, status=400)

#     palabra = data.get("palabra")
#     traduccion = data.get("traduccion")
#     imagen_base64 = data.get("imagen")
#     bbox = data.get("bbox")  # Coordenadas [x1, y1, x2, y2]

#     if not palabra:
#         return JsonResponse({"error": "Falta palabra"}, status=400)

#     # 🧠 Traducir automáticamente si no se pasó traducción
#     if not traduccion or traduccion == "Traducción pendiente":
#         try:
#             traduccion = GoogleTranslator(source="en", target="es").translate(palabra)
#         except Exception as e:
#             traduccion = "Error al traducir"
#             print("❌ Error traduciendo:", e)

#     # 🧩 Evitar duplicados
#     if Flashcard.objects.filter(palabra=palabra).exists():
#         return JsonResponse({"error": "Flashcard ya existe"}, status=400)

#     # 🧱 Crear flashcard
#     flashcard = Flashcard(palabra=palabra, traduccion=traduccion)

#     # 🖼️ Procesar imagen (recortar según bbox si existe)
#     if imagen_base64:
#         try:
#             if ';base64,' in imagen_base64:
#                 _, imgstr = imagen_base64.split(';base64,')
#             else:
#                 imgstr = imagen_base64

#             image_data = base64.b64decode(imgstr)
#             image = Image.open(io.BytesIO(image_data))

#             # 🔹 Recortar si existen coordenadas bbox
#             if bbox and len(bbox) == 4:
#                 x1, y1, x2, y2 = map(int, bbox)
#                 image = image.crop((x1, y1, x2, y2))
#                 print(f"🖼️ Imagen recortada con bbox: {bbox}")
#             else:
#                 print("⚠️ No se recibieron coordenadas bbox, se guarda imagen completa")

#             # 🔹 Guardar imagen en el campo ImageField
#             buffer = io.BytesIO()
#             image.save(buffer, format="PNG")
#             flashcard.imagen.save(
#                 f"{palabra}.png",
#                 ContentFile(buffer.getvalue()),
#                 save=True  # ⚠️ IMPORTANTE: guarda el archivo físicamente
#             )

#         except Exception as e:
#             print("❌ Error procesando imagen:", e)
#             return JsonResponse({"error": f"Error procesando imagen: {str(e)}"}, status=400)
#     else:
#         print("⚠️ No se recibió imagen desde el frontend")

#     # 💾 Guardar registro en la BD
#     flashcard.save()
#     print(f"✅ Flashcard guardada: {flashcard.palabra} ({flashcard.traduccion})")

#     return JsonResponse({
#         "id": flashcard.id,
#         "palabra": flashcard.palabra,
#         "traduccion": flashcard.traduccion,
#         "imagen": flashcard.imagen.url if flashcard.imagen else ""
#     })


# def flashcards_list(request):
#     flashcards = Flashcard.objects.all()
#     data = [
#         {
#             "id": f.id,
#             "palabra": f.palabra,
#             "traduccion": f.traduccion,
#             "imagen": f.imagen.url if f.imagen else ""
#         }
#         for f in flashcards
#     ]
#     return JsonResponse(data, safe=False)


# def review_flashcards(request):
#     today = timezone.now().date()
#     flashcards = Flashcard.objects.filter(next_review__lte=today)
#     data = [
#         {
#             "id": f.id,
#             "palabra": f.palabra,
#             "traduccion": f.traduccion,
#             "imagen": f.imagen.url if f.imagen else ""
#         }
#         for f in flashcards
#     ]
#     return JsonResponse(data, safe=False)






























# @csrf_exempt
# def add_flashcard(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Método no permitido"}, status=405)

#     try:
#         data = json.loads(request.body.decode("utf-8"))
#     except json.JSONDecodeError:
#         return JsonResponse({"error": "Cuerpo no es JSON válido"}, status=400)

#     palabra = data.get("palabra")
#     traduccion = data.get("traduccion")
#     imagen_base64 = data.get("imagen")
#     bbox = data.get("bbox")  # ⬅️ aquí recibimos las coordenadas [x1, y1, x2, y2]

#     if not palabra:
#         return JsonResponse({"error": "Falta palabra"}, status=400)

#     # 🔹 Traducción automática
#     if not traduccion or traduccion == "Traducción pendiente":
#         try:
#             traduccion = GoogleTranslator(source="en", target="es").translate(palabra)
#         except Exception as e:
#             traduccion = "Error al traducir"
#             print("❌ Error traduciendo:", e)

#     # 🔹 Evitar duplicados
#     if Flashcard.objects.filter(palabra=palabra).exists():
#         return JsonResponse({"error": "Flashcard ya existe"}, status=400)

#     flashcard = Flashcard(palabra=palabra, traduccion=traduccion)

#     # 🔹 Procesar imagen y recortar si hay bbox
#     if imagen_base64:
#         try:
#             header, imgstr = imagen_base64.split(';base64,') if ';base64,' in imagen_base64 else (None, imagen_base64)
#             image_data = base64.b64decode(imgstr)
#             image = Image.open(io.BytesIO(image_data))

#             # 🟢 Recortar si hay bounding box
#             if bbox and len(bbox) == 4:
#                 x1, y1, x2, y2 = map(int, bbox)
#                 image = image.crop((x1, y1, x2, y2))
#                 print(f"🖼️ Imagen recortada según bbox: {bbox}")
#             else:
#                 print("⚠️ Sin coordenadas de recorte, se guarda la imagen completa")

#             buffer = io.BytesIO()
#             image.save(buffer, format="PNG")
#             flashcard.imagen.save(
#                 f"{palabra}.png",
#                 ContentFile(buffer.getvalue()),
#                 save=False
#             )
#         except Exception as e:
#             return JsonResponse({"error": f"Error procesando imagen: {str(e)}"}, status=400)

#     flashcard.save()
#     print(f"💾 Flashcard guardada: {flashcard.palabra} ({flashcard.traduccion})")

#     return JsonResponse({
#         "id": flashcard.id,
#         "palabra": flashcard.palabra,
#         "traduccion": flashcard.traduccion
#     })


# def flashcards_list(request):
#     flashcards = Flashcard.objects.all()
#     data = [{"id": f.id, "palabra": f.palabra, "traduccion": f.traduccion} for f in flashcards]
#     return JsonResponse(data, safe=False)


# def review_flashcards(request):
#     today = timezone.now().date()
#     flashcards = Flashcard.objects.filter(next_review__lte=today)
#     data = [
#         {
#             "id": f.id,
#             "palabra": f.palabra,
#             "traduccion": f.traduccion,
#             "imagen": f.imagen.url if f.imagen else ""
#         }
#         for f in flashcards
#     ]
#     return JsonResponse(data, safe=False)
































# @csrf_exempt
# def add_flashcard(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Método no permitido"}, status=405)

#     try:
#         data = json.loads(request.body.decode("utf-8"))
#     except json.JSONDecodeError:
#         return JsonResponse({"error": "Cuerpo no es JSON válido"}, status=400)

#     palabra = data.get("palabra")
#     traduccion = data.get("traduccion")
#     imagen_base64 = data.get("imagen")

#     if not palabra:
#         return JsonResponse({"error": "Falta palabra"}, status=400)

#     # 🔹 Si no hay traducción, traducir automáticamente del inglés al español
#     if not traduccion or traduccion == "Traducción pendiente":
#         try:
#             traduccion = GoogleTranslator(source="en", target="es").translate(palabra)
#         except Exception as e:
#             traduccion = "Error al traducir"
#             print("❌ Error traduciendo:", e)

#     # 🔹 Evitar duplicados
#     if Flashcard.objects.filter(palabra=palabra).exists():
#         return JsonResponse({"error": "Flashcard ya existe"}, status=400)

#     # 🔹 Crear la flashcard
#     flashcard = Flashcard(palabra=palabra, traduccion=traduccion)

#     # 🔹 Procesar imagen si existe
#     if imagen_base64:
#         try:
#             if ';base64,' in imagen_base64:
#                 format, imgstr = imagen_base64.split(';base64,')
#                 ext = format.split('/')[-1]
#             else:
#                 imgstr = imagen_base64
#                 ext = 'png'
#             flashcard.imagen.save(
#                 f"{palabra}.{ext}",
#                 ContentFile(base64.b64decode(imgstr)),
#                 save=False
#             )
#         except Exception as e:
#             return JsonResponse({"error": f"Error procesando imagen: {str(e)}"}, status=400)

#     flashcard.save()
#     print(f"💾 Flashcard guardada: {flashcard.palabra} ({flashcard.traduccion})")

#     return JsonResponse({
#         "id": flashcard.id,
#         "palabra": flashcard.palabra,
#         "traduccion": flashcard.traduccion
#     })


# def flashcards_list(request):
#     flashcards = Flashcard.objects.all()
#     data = [{"id": f.id, "palabra": f.palabra, "traduccion": f.traduccion} for f in flashcards]
#     return JsonResponse(data, safe=False)


# def review_flashcards(request):
#     today = timezone.now().date()
#     flashcards = Flashcard.objects.filter(next_review__lte=today)
#     data = [
#         {
#             "id": f.id,
#             "palabra": f.palabra,
#             "traduccion": f.traduccion,
#             "imagen": f.imagen.url if f.imagen else ""
#         }
#         for f in flashcards
#     ]
#     return JsonResponse(data, safe=False)
