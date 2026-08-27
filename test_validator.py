import sys
import os
import json

import cv2
import numpy as np
import tensorflow as tf


# ============================================================
# USAGE
# ============================================================

if len(sys.argv) != 2:
    print()
    print("Usage:")
    print("python test_validator.py <image_path>")
    print()
    print("Example:")
    print(
        r'python test_validator.py "validator_dataset\Bell_Pepper\image.jpg"'
    )
    sys.exit(1)


IMAGE_PATH = sys.argv[1]


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "plant_validator.keras"
)

CLASS_NAMES_PATH = os.path.join(
    BASE_DIR,
    "models",
    "plant_validator_classes.json"
)


# ============================================================
# CHECK FILES
# ============================================================

if not os.path.exists(MODEL_PATH):
    print("ERROR: Validator model not found:")
    print(MODEL_PATH)
    sys.exit(1)


if not os.path.exists(CLASS_NAMES_PATH):
    print("ERROR: Class names file not found:")
    print(CLASS_NAMES_PATH)
    sys.exit(1)


if not os.path.exists(IMAGE_PATH):
    print("ERROR: Image not found:")
    print(IMAGE_PATH)
    sys.exit(1)


# ============================================================
# LOAD CLASS NAMES
# ============================================================

with open(
    CLASS_NAMES_PATH,
    "r"
) as file:

    class_names = json.load(file)


print()
print("=" * 60)
print("PLANT VALIDATOR DIAGNOSTIC")
print("=" * 60)

print()
print("Model:")
print(MODEL_PATH)

print()
print("Image:")
print(os.path.abspath(IMAGE_PATH))

print()
print("Classes:")
print(class_names)


# ============================================================
# LOAD MODEL
# ============================================================

print()
print("Loading validator model...")

model = tf.keras.models.load_model(
    MODEL_PATH
)

print("Model loaded successfully.")


# ============================================================
# LOAD IMAGE
# ============================================================

image = cv2.imread(
    IMAGE_PATH
)

if image is None:

    print()
    print("ERROR: OpenCV could not read the image.")
    sys.exit(1)


image = cv2.cvtColor(
    image,
    cv2.COLOR_BGR2RGB
)


print()
print("Original image shape:")
print(image.shape)


# ============================================================
# PREPROCESS
# ============================================================

image = cv2.resize(
    image,
    (224, 224),
    interpolation=cv2.INTER_AREA
)

image = image.astype(
    np.float32
)

image = np.expand_dims(
    image,
    axis=0
)


# ============================================================
# PREDICTION
# ============================================================

prediction = model.predict(
    image,
    verbose=0
)

prediction = np.asarray(
    prediction,
    dtype=np.float32
).flatten()


# ============================================================
# OUTPUT VALIDATION
# ============================================================

print()
print("Model output count:")
print(len(prediction))

print()
print("Class count:")
print(len(class_names))


if len(prediction) != len(class_names):

    print()
    print("ERROR:")
    print(
        "Model output count does not match class count."
    )

    sys.exit(1)


# ============================================================
# DISPLAY ALL PROBABILITIES
# ============================================================

print()
print("=" * 60)
print("CLASS PROBABILITIES")
print("=" * 60)

for index, class_name in enumerate(class_names):

    probability = (
        float(prediction[index]) * 100
    )

    print(
        f"{class_name:<15} : {probability:8.4f}%"
    )


# ============================================================
# FINAL PREDICTION
# ============================================================

best_index = int(
    np.argmax(prediction)
)

best_class = class_names[
    best_index
]

best_confidence = (
    float(prediction[best_index]) * 100
)


print()
print("=" * 60)
print("FINAL PREDICTION")
print("=" * 60)

print()
print("Predicted class:")
print(best_class)

print()
print("Confidence:")
print(
    f"{best_confidence:.4f}%"
)


# ============================================================
# TOP 3
# ============================================================

top_indices = np.argsort(
    prediction
)[::-1][:3]


print()
print("Top 3 predictions:")

for rank, index in enumerate(
    top_indices,
    start=1
):

    print(
        f"{rank}. "
        f"{class_names[int(index)]} "
        f"({float(prediction[index]) * 100:.4f}%)"
    )


print()
print("=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)