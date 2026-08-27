import tensorflow as tf
import numpy as np
from PIL import Image

MODEL_PATH = "models/plant_validator.keras"

model = tf.keras.models.load_model(MODEL_PATH)

print("MODEL LOADED")
print("Input shape:", model.input_shape)
print("Output shape:", model.output_shape)

IMAGE_PATH = r"C:\Users\Mohammed Taha\OneDrive\Pictures\Chartwork\banana.jpg"

image = Image.open(IMAGE_PATH).convert("RGB")
image = image.resize((224, 224))

image_array = np.array(
    image,
    dtype=np.float32
) / 255.0

image_array = np.expand_dims(
    image_array,
    axis=0
)

prediction = model.predict(
    image_array,
    verbose=0
)[0]

print()
print("RAW PREDICTIONS:")
print(prediction)

print()
print("PREDICTION SUM:")
print(np.sum(prediction))

print()
print("WINNING INDEX:")
print(np.argmax(prediction))

print()
print("WINNING CONFIDENCE:")
print(float(np.max(prediction) * 100))