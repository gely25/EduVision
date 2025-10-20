from ultralytics import YOLO

# ✅ Ruta del dataset
DATASET_PATH = r"C:\EduVision\src\infrastructure\ai_models\datasets\data.yaml"

# ✅ Cargar modelo YOLOv8 preentrenado (base nano, ideal para CPU)
model = YOLO("yolov8n.pt")

# 🚀 Fine-tuning: entrenar el modelo base con tus datos personalizados
model.train(
    data=DATASET_PATH,       # tu dataset personalizado
    epochs=25,               # número de pasadas (ajusta si quieres más)
    imgsz=640,               # resolución de entrenamiento
    batch=8,                 # tamaño del lote
    pretrained=True,         # 👈 usa conocimiento previo del modelo
    name="stationery_finetune",  # carpeta de resultados
    verbose=True
)

print("✅ Entrenamiento completado. Modelo guardado en 'runs/detect/stationery_finetune/weights/best.pt'")
