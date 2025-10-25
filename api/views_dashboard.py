# api/views_dashboard.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from src.infrastructure.orm.flashcards.models import Flashcard
from django.http import JsonResponse


@login_required
def dashboard_view(request):
    """
    Muestra el panel del usuario logueado con sus estadísticas de flashcards.
    """
    user = request.user
    today = timezone.now().date()

    # 🔹 Solo las flashcards del usuario
    user_cards = Flashcard.objects.filter(user=user)

    # 🔸 Pendientes y aprendidas según la fecha de repaso
    pending_qs = user_cards.filter(next_review__lte=today)
    mastered_qs = user_cards.filter(next_review__gt=today)

    context = {
        "nombre": user.first_name or user.username,
        "aprendidas": mastered_qs.count(),
        "pendientes": pending_qs.count(),
        "total": user_cards.count(),
    }

    return render(request, "dashboard.html", context)


@login_required
def dashboard_summary_api(request):
    """
    Endpoint para obtener los contadores actualizados sin recargar.
    """
    today = timezone.now().date()
    user = request.user
    user_cards = Flashcard.objects.filter(user=user)

    pending_qs = user_cards.filter(next_review__lte=today)
    mastered_qs = user_cards.filter(next_review__gt=today)

    data = {
        "counters": {
            "pendientes": pending_qs.count(),
            "aprendidas": mastered_qs.count(),
            "total": user_cards.count(),
        }
    }
    return JsonResponse(data)
