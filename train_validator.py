import os
import json
import tensorflow as tf

from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import (
    EarlyStopping,
    ReduceLROnPlateau,
    ModelCheckpoint
)


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_DIR = "validator_dataset"

MODEL_DIR = "models"

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "plant_validator.keras"
)

CLASS_NAMES_PATH = os.path.join(
    MODEL_DIR,
    "plant_validator_classes.json"
)

IMAGE_SIZE = (224, 224)

BATCH_SIZE = 32

EPOCHS = 15

VALIDATION_SPLIT = 0.20

SEED = 42


# ============================================================
# CREATE MODEL DIRECTORY
# ============================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ============================================================
# CHECK DATASET
# ============================================================

required_classes = [
    "Tomato",
    "Potato",
    "Bell_Pepper",
    "Other"
]

print()
print("=" * 60)
print("CHECKING VALIDATOR DATASET")
print("=" * 60)

for class_name in required_classes:

    class_path = os.path.join(
        DATASET_DIR,
        class_name
    )

    if not os.path.isdir(class_path):

        raise FileNotFoundError(
            f"Missing dataset folder: {class_path}"
        )

    image_count = len([
        file
        for file in os.listdir(class_path)
        if file.lower().endswith(
            (".jpg", ".jpeg", ".png")
        )
    ])

    print(
        f"{class_name}: {image_count} images"
    )


# ============================================================
# LOAD DATASET
# ============================================================

print()
print("=" * 60)
print("LOADING DATASET")
print("=" * 60)

train_dataset = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=VALIDATION_SPLIT,
    subset="training",
    seed=SEED,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="categorical",
    class_names=required_classes
)

validation_dataset = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=VALIDATION_SPLIT,
    subset="validation",
    seed=SEED,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="categorical",
    class_names=required_classes
)


# ============================================================
# SAVE CLASS NAMES
# ============================================================

class_names = train_dataset.class_names

print()
print("Classes:")
print(class_names)

with open(
    CLASS_NAMES_PATH,
    "w"
) as file:

    json.dump(
        class_names,
        file,
        indent=4
    )


# ============================================================
# PERFORMANCE OPTIMIZATION
# ============================================================

AUTOTUNE = tf.data.AUTOTUNE

train_dataset = train_dataset.prefetch(
    AUTOTUNE
)

validation_dataset = validation_dataset.prefetch(
    AUTOTUNE
)


# ============================================================
# DATA AUGMENTATION
# ============================================================

data_augmentation = tf.keras.Sequential(
    [
        layers.RandomFlip(
            "horizontal"
        ),

        layers.RandomRotation(
            0.10
        ),

        layers.RandomZoom(
            0.10
        ),

        layers.RandomContrast(
            0.10
        )
    ],
    name="data_augmentation"
)


# ============================================================
# BASE MODEL
# ============================================================

base_model = MobileNetV2(
    input_shape=(
        IMAGE_SIZE[0],
        IMAGE_SIZE[1],
        3
    ),

    include_top=False,

    weights="imagenet"
)


# Freeze pretrained layers
base_model.trainable = False


# ============================================================
# BUILD VALIDATOR
# ============================================================

inputs = layers.Input(
    shape=(
        IMAGE_SIZE[0],
        IMAGE_SIZE[1],
        3
    )
)


x = data_augmentation(
    inputs
)


x = tf.keras.applications.mobilenet_v2.preprocess_input(
    x
)


x = base_model(
    x,
    training=False
)


x = layers.GlobalAveragePooling2D()(x)


x = layers.Dropout(
    0.30
)(x)


x = layers.Dense(
    128,
    activation="relu"
)(x)


x = layers.Dropout(
    0.20
)(x)


outputs = layers.Dense(
    len(class_names),
    activation="softmax"
)(x)


model = models.Model(
    inputs,
    outputs
)


# ============================================================
# COMPILE
# ============================================================

model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=0.0001
    ),

    loss="categorical_crossentropy",

    metrics=[
        "accuracy"
    ]
)


# ============================================================
# CALLBACKS
# ============================================================

callbacks = [

    EarlyStopping(
        monitor="val_accuracy",
        patience=4,
        restore_best_weights=True
    ),

    ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=2,
        min_lr=0.000001
    ),

    ModelCheckpoint(
        MODEL_PATH,
        monitor="val_accuracy",
        save_best_only=True
    )
]


# ============================================================
# MODEL SUMMARY
# ============================================================

print()
print("=" * 60)
print("MODEL")
print("=" * 60)

model.summary()


# ============================================================
# TRAIN
# ============================================================

print()
print("=" * 60)
print("STARTING TRAINING")
print("=" * 60)

history = model.fit(
    train_dataset,

    validation_data=validation_dataset,

    epochs=EPOCHS,

    callbacks=callbacks
)


# ============================================================
# FINAL EVALUATION
# ============================================================

print()
print("=" * 60)
print("FINAL VALIDATION")
print("=" * 60)

loss, accuracy = model.evaluate(
    validation_dataset
)

print(
    f"Validation accuracy: "
    f"{accuracy * 100:.2f}%"
)


# ============================================================
# SAVE FINAL MODEL
# ============================================================

model.save(
    MODEL_PATH
)

print()
print("=" * 60)
print("TRAINING COMPLETE")
print("=" * 60)

print(
    f"Model saved to:"
)

print(
    os.path.abspath(
        MODEL_PATH
    )
)

print()

print(
    "Classes saved to:"
)

print(
    os.path.abspath(
        CLASS_NAMES_PATH
    )
)