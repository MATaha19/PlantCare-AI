import os
import json
import shutil
import random

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

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATASET_DIR = os.path.join(
    BASE_DIR,
    "validator_dataset"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "plant_validator.keras"
)

CLASS_NAMES_PATH = os.path.join(
    MODEL_DIR,
    "plant_validator_classes.json"
)

IMAGE_SIZE = (
    224,
    224
)

BATCH_SIZE = 32

SEED = 42

EPOCHS_HEAD = 10

EPOCHS_FINE = 10


CLASS_NAMES = [
    "Tomato",
    "Potato",
    "Bell_Pepper",
    "Other"
]


# ============================================================
# RANDOM SEED
# ============================================================

random.seed(SEED)

tf.random.set_seed(
    SEED
)


# ============================================================
# CHECK DATASET
# ============================================================

print()
print("=" * 70)
print("PLANTCARE AI — PLANT VALIDATOR TRAINING")
print("=" * 70)

print()
print("Dataset:")
print(DATASET_DIR)

if not os.path.exists(DATASET_DIR):

    raise FileNotFoundError(
        f"Dataset not found: {DATASET_DIR}"
    )


for class_name in CLASS_NAMES:

    class_dir = os.path.join(
        DATASET_DIR,
        class_name
    )

    if not os.path.isdir(class_dir):

        raise FileNotFoundError(
            f"Missing dataset class folder: {class_dir}"
        )


# ============================================================
# SHOW DATASET COUNTS
# ============================================================

print()
print("Dataset class counts:")

total_images = 0

for class_name in CLASS_NAMES:

    class_dir = os.path.join(
        DATASET_DIR,
        class_name
    )

    count = 0

    for root, _, files in os.walk(
        class_dir
    ):

        for filename in files:

            extension = (
                os.path.splitext(filename)[1]
                .lower()
            )

            if extension in [
                ".jpg",
                ".jpeg",
                ".png",
                ".bmp",
                ".webp"
            ]:

                count += 1


    total_images += count

    print(
        f"{class_name:<15} : {count}"
    )


print(
    f"{'TOTAL':<15} : {total_images}"
)


# ============================================================
# CREATE TRAIN / VALIDATION / TEST SPLIT
# ============================================================

SPLIT_DIR = os.path.join(
    BASE_DIR,
    "validator_split"
)


TRAIN_DIR = os.path.join(
    SPLIT_DIR,
    "train"
)

VAL_DIR = os.path.join(
    SPLIT_DIR,
    "validation"
)

TEST_DIR = os.path.join(
    SPLIT_DIR,
    "test"
)


# ------------------------------------------------------------
# Remove previous split
# ------------------------------------------------------------

if os.path.exists(
    SPLIT_DIR
):

    print()
    print(
        "Removing previous validator split..."
    )

    shutil.rmtree(
        SPLIT_DIR
    )


os.makedirs(
    TRAIN_DIR
)

os.makedirs(
    VAL_DIR
)

os.makedirs(
    TEST_DIR
)


# ============================================================
# SPLIT DATA
# ============================================================

TRAIN_RATIO = 0.70

VAL_RATIO = 0.15

TEST_RATIO = 0.15


print()
print("=" * 70)
print("CREATING DATASET SPLIT")
print("=" * 70)


for class_name in CLASS_NAMES:

    source_dir = os.path.join(
        DATASET_DIR,
        class_name
    )


    train_class_dir = os.path.join(
        TRAIN_DIR,
        class_name
    )

    val_class_dir = os.path.join(
        VAL_DIR,
        class_name
    )

    test_class_dir = os.path.join(
        TEST_DIR,
        class_name
    )


    os.makedirs(
        train_class_dir
    )

    os.makedirs(
        val_class_dir
    )

    os.makedirs(
        test_class_dir
    )


    files = []


    for root, _, filenames in os.walk(
        source_dir
    ):

        for filename in filenames:

            extension = (
                os.path.splitext(filename)[1]
                .lower()
            )

            if extension in [
                ".jpg",
                ".jpeg",
                ".png",
                ".bmp",
                ".webp"
            ]:

                files.append(
                    os.path.join(
                        root,
                        filename
                    )
                )


    random.shuffle(
        files
    )


    total = len(
        files
    )


    train_end = int(
        total * TRAIN_RATIO
    )

    val_end = train_end + int(
        total * VAL_RATIO
    )


    train_files = files[
        :train_end
    ]

    val_files = files[
        train_end:val_end
    ]

    test_files = files[
        val_end:
    ]


    for source_file in train_files:

        destination = os.path.join(
            train_class_dir,
            os.path.basename(
                source_file
            )
        )

        shutil.copy2(
            source_file,
            destination
        )


    for source_file in val_files:

        destination = os.path.join(
            val_class_dir,
            os.path.basename(
                source_file
            )
        )

        shutil.copy2(
            source_file,
            destination
        )


    for source_file in test_files:

        destination = os.path.join(
            test_class_dir,
            os.path.basename(
                source_file
            )
        )

        shutil.copy2(
            source_file,
            destination
        )


    print(
        f"{class_name:<15} "
        f"Train: {len(train_files):4d} | "
        f"Validation: {len(val_files):4d} | "
        f"Test: {len(test_files):4d}"
    )


# ============================================================
# LOAD DATASETS
# ============================================================

print()
print(
    "Loading TensorFlow datasets..."
)


train_dataset = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    labels="inferred",
    label_mode="categorical",
    class_names=CLASS_NAMES,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=True,
    seed=SEED
)


validation_dataset = tf.keras.utils.image_dataset_from_directory(
    VAL_DIR,
    labels="inferred",
    label_mode="categorical",
    class_names=CLASS_NAMES,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)


test_dataset = tf.keras.utils.image_dataset_from_directory(
    TEST_DIR,
    labels="inferred",
    label_mode="categorical",
    class_names=CLASS_NAMES,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)


# ============================================================
# PERFORMANCE
# ============================================================

AUTOTUNE = (
    tf.data.AUTOTUNE
)


train_dataset = train_dataset.prefetch(
    AUTOTUNE
)

validation_dataset = validation_dataset.prefetch(
    AUTOTUNE
)

test_dataset = test_dataset.prefetch(
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

print()
print(
    "Loading MobileNetV2..."
)


base_model = MobileNetV2(
    input_shape=(
        IMAGE_SIZE[0],
        IMAGE_SIZE[1],
        3
    ),

    include_top=False,

    weights="imagenet"
)


base_model.trainable = False


# ============================================================
# CLASSIFIER
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


x = layers.Rescaling(
    1.0 / 127.5,
    offset=-1
)(
    x
)


x = base_model(
    x,
    training=False
)


x = layers.GlobalAveragePooling2D()(
    x
)


x = layers.Dropout(
    0.30
)(
    x
)


outputs = layers.Dense(
    len(CLASS_NAMES),
    activation="softmax"
)(
    x
)


model = models.Model(
    inputs,
    outputs
)


# ============================================================
# COMPILE — HEAD TRAINING
# ============================================================

model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=0.001
    ),

    loss="categorical_crossentropy",

    metrics=[
        "accuracy"
    ]
)


# ============================================================
# CALLBACKS
# ============================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


checkpoint = ModelCheckpoint(
    MODEL_PATH,
    monitor="val_accuracy",
    save_best_only=True,
    verbose=1
)


early_stopping = EarlyStopping(
    monitor="val_accuracy",
    patience=4,
    restore_best_weights=True,
    verbose=1
)


reduce_lr = ReduceLROnPlateau(
    monitor="val_loss",
    factor=0.3,
    patience=2,
    min_lr=1e-7,
    verbose=1
)


# ============================================================
# TRAIN CLASSIFICATION HEAD
# ============================================================

print()
print("=" * 70)
print("PHASE 1 — TRAINING CLASSIFICATION HEAD")
print("=" * 70)


model.fit(
    train_dataset,

    validation_data=validation_dataset,

    epochs=EPOCHS_HEAD,

    callbacks=[
        checkpoint,
        early_stopping,
        reduce_lr
    ]
)


# ============================================================
# FINE-TUNING
# ============================================================

print()
print("=" * 70)
print("PHASE 2 — FINE-TUNING MOBILENETV2")
print("=" * 70)


base_model.trainable = True


# Freeze the majority of the base model.
# Only the final layers are fine-tuned.

for layer in base_model.layers[:-30]:

    layer.trainable = False


model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=0.00001
    ),

    loss="categorical_crossentropy",

    metrics=[
        "accuracy"
    ]
)


model.fit(
    train_dataset,

    validation_data=validation_dataset,

    epochs=EPOCHS_FINE,

    callbacks=[
        checkpoint,
        early_stopping,
        reduce_lr
    ]
)


# ============================================================
# LOAD BEST MODEL
# ============================================================

print()
print(
    "Loading best validator model..."
)


best_model = tf.keras.models.load_model(
    MODEL_PATH
)


# ============================================================
# TEST SET EVALUATION
# ============================================================

print()
print("=" * 70)
print("FINAL TEST SET EVALUATION")
print("=" * 70)


test_loss, test_accuracy = (
    best_model.evaluate(
        test_dataset,
        verbose=1
    )
)


print()
print(
    f"Test loss     : {test_loss:.4f}"
)

print(
    f"Test accuracy : {test_accuracy * 100:.2f}%"
)


# ============================================================
# SAVE CLASS NAMES
# ============================================================

with open(
    CLASS_NAMES_PATH,
    "w"
) as file:

    json.dump(
        CLASS_NAMES,
        file,
        indent=4
    )


# ============================================================
# SAVE FINAL MODEL
# ============================================================

best_model.save(
    MODEL_PATH
)


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 70)
print("VALIDATOR TRAINING COMPLETE")
print("=" * 70)

print()
print("Model:")
print(MODEL_PATH)

print()
print("Class names:")
print(CLASS_NAMES_PATH)

print()
print(
    f"Final test accuracy: "
    f"{test_accuracy * 100:.2f}%"
)

print()
print("Classes:")

for index, class_name in enumerate(
    CLASS_NAMES
):

    print(
        f"{index} → {class_name}"
    )

print()
print("Next step:")
print(
    "Run test_validator.py against "
    "Bell Pepper, Tomato, Potato, "
    "and an Other image."
)