from django.urls import path
from . import views_flashcards

urlpatterns = [
    path("flashcards/add/", views_flashcards.add_flashcard, name="add_flashcard"),
    path("flashcards/list/", views_flashcards.flashcards_list, name="flashcards_list"),
    path("flashcards/review/", views_flashcards.review_flashcards, name="review_flashcards"),
    path("flashcards/<int:id>/mark/", views_flashcards.mark_flashcard, name="mark_flashcard"),  
    path("flashcards/review/page/", views_flashcards.review_page, name="review_page"),

]

