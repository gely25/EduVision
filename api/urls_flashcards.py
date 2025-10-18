from django.urls import path
from . import views_flashcards

urlpatterns = [
    # API
    path("flashcards/add/", views_flashcards.add_flashcard, name="add_flashcard"),
    path("flashcards/list/", views_flashcards.flashcards_list, name="flashcards_list"),
    path("flashcards/review/", views_flashcards.review_flashcards, name="review_flashcards"),
    path("flashcards/summary/", views_flashcards.flashcards_summary, name="flashcards_summary"),
    path("flashcards/<int:id>/mark/", views_flashcards.mark_flashcard, name="mark_flashcard"),


    # Páginas
    path("flashcards/page/", views_flashcards.flashcards_page, name="flashcards_page"),
    path("flashcards/review/page/", views_flashcards.flashcards_review_page, name="flashcards_review_page"),
]

