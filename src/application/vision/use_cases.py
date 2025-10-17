from src.infrastructure.ai_models import object_detector

class GetDetectedObjectsUC:
    def __call__(self):
        return object_detector.get_detected_objects_with_images()
