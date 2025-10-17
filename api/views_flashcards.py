from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from src.infrastructure.orm.flashcards.models import Flashcard

from django.utils import timezone
import json
import base64
from django.core.files.base import ContentFile

@csrf_exempt
def add_flashcard(request):
    if request.method == "POST":
        data = json.loads(request.body)
        palabra = data.get("palabra")
        traduccion = data.get("traduccion")
        imagen_base64 = data.get("imagen")

        if not palabra or not traduccion:
            return JsonResponse({"error": "Falta palabra o traducción"}, status=400)

        if Flashcard.objects.filter(palabra=palabra).exists():
            return JsonResponse({"error": "Flashcard ya existe"}, status=400)

        flashcard = Flashcard(palabra=palabra, traduccion=traduccion)

        # Guardar imagen si existe
        if imagen_base64:
            try:
                if ';base64,' in imagen_base64:
                    format, imgstr = imagen_base64.split(';base64,')
                    ext = format.split('/')[-1]
                else:
                    imgstr = imagen_base64
                    ext = 'png'
                flashcard.imagen.save(
                    f"{palabra}.{ext}",
                    ContentFile(base64.b64decode(imgstr)),
                    save=False
                )
            except Exception as e:
                return JsonResponse({"error": f"Error procesando imagen: {str(e)}"}, status=400)

        flashcard.save()

        return JsonResponse({
            "id": flashcard.id,
            "palabra": flashcard.palabra,
            "traduccion": flashcard.traduccion
        })


def flashcards_list(request):
    flashcards = Flashcard.objects.all()
    data = [{"id": f.id, "palabra": f.palabra, "traduccion": f.traduccion} for f in flashcards]
    return JsonResponse(data, safe=False)


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
