import os
import numpy as np
import tensorflow as tf


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "plant_validator.keras"
)

TEST_DIR = os.path.join(
    BASE_DIR,
    "validator_split",
    "test"
)

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32

CLASS_NAMES = [
    "Tomato",
    "Potato",
    "Bell_Pepper",
    "Other"
]


print("=" * 70)
print("PLANT VALIDATOR — CLASS-BY-CLASS TEST")
print("=" * 70)

print()
print("Loading model...")

model = tf.keras.models.load_model(
    MODEL_PATH
)

print("Model loaded.")


test_dataset = tf.keras.utils.image_dataset_from_directory(
    TEST_DIR,
    labels="inferred",
    label_mode="int",
    class_names=CLASS_NAMES,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)


correct = {
    class_name: 0
    for class_name in CLASS_NAMES
}

total = {
    class_name: 0
    for class_name in CLASS_NAMES
}

confusion = np.zeros(
    (
        len(CLASS_NAMES),
        len(CLASS_NAMES)
    ),
    dtype=int
)


for images, labels in test_dataset:

    predictions = model.predict(
        images,
        verbose=0
    )

    predicted_labels = np.argmax(
        predictions,
        axis=1
    )

    for actual, predicted in zip(
        labels.numpy(),
        predicted_labels
    ):

        actual = int(actual)
        predicted = int(predicted)

        total[
            CLASS_NAMES[actual]
        ] += 1

        confusion[
            actual,
            predicted
        ] += 1

        if actual == predicted:

            correct[
                CLASS_NAMES[actual]
            ] += 1


print()
print("=" * 70)
print("PER-CLASS ACCURACY")
print("=" * 70)

for class_name in CLASS_NAMES:

    count = total[class_name]

    accuracy = (
        correct[class_name] /
        count *
        100
        if count > 0
        else 0
    )

    print(
        f"{class_name:<15} "
        f"{correct[class_name]:4d}/"
        f"{count:<4d} "
        f"({accuracy:6.2f}%)"
    )


print()
print("=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)

print()
print(
    f"{'Actual':<15}",
    end=""
)

for class_name in CLASS_NAMES:

    print(
        f"{class_name:<15}",
        end=""
    )

print()

for i, class_name in enumerate(
    CLASS_NAMES
):

    print(
        f"{class_name:<15}",
        end=""
    )

    for j in range(
        len(CLASS_NAMES)
    ):

        print(
            f"{confusion[i, j]:<15}",
            end=""
        )

    print()


print()
print("=" * 70)
print("IMPORTANT BELL PEPPER CHECK")
print("=" * 70)

bell_pepper_index = (
    CLASS_NAMES.index(
        "Bell_Pepper"
    )
)

print()

print(
    "Actual Bell Pepper images:"
)

print(
    total["Bell_Pepper"]
)

print()

print(
    "Correctly predicted Bell Pepper:"
)

print(
    correct["Bell_Pepper"]
)

print()

print(
    "Bell Pepper predictions:"
)

for index, class_name in enumerate(
    CLASS_NAMES
):

    print(
        f"  → {class_name}: "
        f"{confusion[bell_pepper_index, index]}"
    )


print()
print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)