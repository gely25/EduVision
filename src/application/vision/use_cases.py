from src.infrastructure.ai_models import orb_recognizer

class GetDetectedObjectsUC:
    def __call__(self):
        return orb_recognizer.get_detected_objects_with_images()
