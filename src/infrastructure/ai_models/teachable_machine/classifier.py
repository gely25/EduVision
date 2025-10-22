import cv2
import tensorflow as tf
from keras.layers import TFSMLayer
import numpy as np

# Etiquetas según tu modelo
CLASS_NAMES = ["Pencil", "Notebook", "Calculator"]

# Cargar modelo Teachable Machine
LAYER = TFSMLayer(
    "src/infrastructure/ai_models/teachable_machine/model.savedmodel",
    call_endpoint="serving_default"
)

def classify_frame(frame):
    """Clasifica un frame BGR y devuelve (etiqueta, confianza)"""
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (224, 224))
    img_norm = img_resized / 255.0
    x = tf.convert_to_tensor(img_norm, dtype=tf.float32)
    x = tf.expand_dims(x, axis=0)

    y = LAYER(x)
    if isinstance(y, dict):
        y = list(y.values())[0]
    output = y.numpy()[0]

    idx = int(np.argmax(output))
    return CLASS_NAMES[idx], float(output[idx])
