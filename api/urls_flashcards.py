from django.urls import path
from . import views_flashcards

urlpatterns = [
    path("flashcards/add/", views_flashcards.add_flashcard, name="add_flashcard"),
    path("flashcards/list/", views_flashcards.flashcards_list, name="flashcards_list"),
    path("flashcards/review/", views_flashcards.review_flashcards, name="review_flashcards"),
]
