# src/infrastructure/orm/flashcards/models.py
from django.db import models
from django.utils import timezone

class Flashcard(models.Model):
    palabra = models.CharField(max_length=100, unique=True)
    traduccion = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to="flashcards/", null=True, blank=True)
    next_review = models.DateField(default=timezone.now)
    interval = models.IntegerField(default=1)

    def __str__(self):
        return self.palabra
