# src/infrastructure/ai_models/model_trainer.py

import os
from ultralytics import YOLO


class YOLOTrainer:
    """
    Servicio de entrenamiento para modelos YOLOv8.
    Permite reentrenar desde un modelo base con datasets nuevos.
    """

    def __init__(self, base_model_path="yolov8n.pt"):
        self.base_model_path = base_model_path

    def train_model(self, dataset_path, epochs=15, project_name="EduVisionTrain"):
        """
        dataset_path: ruta al data.yaml (Roboflow exportado)
        epochs: número de iteraciones de entrenamiento
        project_name: nombre del proyecto (para guardar pesos)
        """
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"No se encontró el dataset en {dataset_path}")

        print(f"🚀 Iniciando entrenamiento con dataset: {dataset_path}")
        model = YOLO(self.base_model_path)

        results = model.train(
            data=dataset_path,
            epochs=epochs,
            project="models",
            name=project_name,
            exist_ok=True
        )

        # Ruta del mejor modelo generado
        best_model = os.path.join("models", project_name, "weights", "best.pt")

        if not os.path.exists(best_model):
            raise FileNotFoundError("❌ No se generó el modelo entrenado correctamente.")

        print(f"✅ Entrenamiento completado. Modelo guardado en: {best_model}")
        return best_model
