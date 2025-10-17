def process_detected_objects(detector_service):
    """
    Obtiene etiquetas e imágenes detectadas desde el servicio de IA.
    """
    return detector_service.get_detected_objects_with_images()
