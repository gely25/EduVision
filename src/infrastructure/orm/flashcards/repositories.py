# src/infrastructure/orm/flashcards/repositories.py
from src.domain.flashcards.entities import FlashcardEntity
from src.infrastructure.orm.flashcards.models import Flashcard

class FlashcardRepository:
    def to_entity(self, model):
        return FlashcardEntity(
            id=model.id,
            palabra=model.palabra,
            traduccion=model.traduccion,
            imagen=model.imagen.url if model.imagen else None,
            next_review=model.next_review,
            interval=model.interval,
        )

    def save(self, entity):
        obj, _ = Flashcard.objects.update_or_create(
            id=entity.id,
            defaults={
                "palabra": entity.palabra,
                "traduccion": entity.traduccion,
                "next_review": entity.next_review,
                "interval": entity.interval,
            },
        )
        return self.to_entity(obj)

    def get_by_id(self, id):
        try:
            model = Flashcard.objects.get(id=id)
            return self.to_entity(model)
        except Flashcard.DoesNotExist:
            return None

    def get_due_today(self):
        from django.utils import timezone
        today = timezone.now().date()
        return [
            self.to_entity(f)
            for f in Flashcard.objects.filter(next_review__lte=today)
        ]
