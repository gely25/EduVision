# src/domain/flashcards/entities.py
from datetime import date, timedelta

class FlashcardEntity:
    def __init__(self, palabra, traduccion, imagen=None, interval=1, next_review=None, id=None):
        self.id = id
        self.palabra = palabra
        self.traduccion = traduccion
        self.imagen = imagen
        self.interval = interval
        self.next_review = next_review or date.today()

    def mark_reviewed(self, success=True):
        """Actualiza la fecha de revisión y el intervalo según la respuesta del usuario."""
        if success:
            self.interval *= 2
        else:
            self.interval = 1
        self.next_review = date.today() + timedelta(days=self.interval)
