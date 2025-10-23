from django.urls import path
from api import views_flashcards

urlpatterns = [
    # API endpoints
    path("add/", views_flashcards.add_flashcard, name="add_flashcard"),
    path("list/", views_flashcards.flashcards_list, name="flashcards_list"),
    path("review/", views_flashcards.review_flashcards, name="review_flashcards"),
    path("summary/", views_flashcards.flashcards_summary, name="flashcards_summary"),
    path("<int:id>/mark/", views_flashcards.mark_flashcard, name="mark_flashcard"),

    # Páginas
    path("page/", views_flashcards.flashcards_page, name="flashcards_page"),
    path("review/page/", views_flashcards.flashcards_review_page, name="flashcards_review_page"),
]
