# src/application/vision/train_model_use_case.py

from src.infrastructure.ai_models.model_trainer import YOLOTrainer


class TrainModelUseCase:
    """
    Caso de uso para lanzar el entrenamiento desde la capa de aplicación.
    """

    def __init__(self):
        self.trainer = YOLOTrainer()

    def execute(self, dataset_path: str, epochs: int = 15):
        try:
            model_path = self.trainer.train_model(dataset_path, epochs)
            return {"status": "success", "model_path": model_path}
        except Exception as e:
            return {"status": "error", "message": str(e)}
