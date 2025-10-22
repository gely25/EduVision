# src/application/flashcards/use_cases.py

def get_flashcards_due_today(repository):
    """Obtiene las tarjetas que deben revisarse hoy."""
    return repository.get_due_today()


def mark_flashcard_reviewed(repository, id, success):
    """Marca una flashcard como recordada u olvidada."""
    flashcard = repository.get_by_id(id)
    if not flashcard:
        return None
    flashcard.mark_reviewed(success)
    repository.save(flashcard)
    return flashcard
