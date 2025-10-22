from django.contrib import admin
from .models import Flashcard


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ("palabra", "traduccion", "next_review", "interval")
    search_fields = ("palabra", "traduccion")
    list_filter = ("next_review",)
    ordering = ("next_review",)
