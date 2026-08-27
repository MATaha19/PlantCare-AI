import os
import shutil
import random


# ============================================================
# SETTINGS
# ============================================================

SOURCE_DIR = "PlantVillage"
OUTPUT_DIR = "validator_dataset"

SAMPLES_PER_PLANT = 1000


# ============================================================
# CREATE OUTPUT FOLDERS
# ============================================================

classes = [
    "Tomato",
    "Potato",
    "Bell_Pepper"
]

for class_name in classes:

    os.makedirs(
        os.path.join(
            OUTPUT_DIR,
            class_name
        ),
        exist_ok=True
    )


# ============================================================
# FIND IMAGES
# ============================================================

image_extensions = (
    ".jpg",
    ".jpeg",
    ".png",
    ".JPG",
    ".JPEG",
    ".PNG"
)


def collect_images(folder):

    images = []

    for root, dirs, files in os.walk(folder):

        for file in files:

            if file.endswith(
                image_extensions
            ):

                images.append(
                    os.path.join(
                        root,
                        file
                    )
                )

    return images


# ============================================================
# COLLECT PLANTVILLAGE IMAGES
# ============================================================

all_images = collect_images(
    SOURCE_DIR
)

print(
    f"\nFound {len(all_images)} images "
    f"in PlantVillage."
)


# ============================================================
# IDENTIFY PLANT
# ============================================================

plant_images = {

    "Tomato": [],

    "Potato": [],

    "Bell_Pepper": []
}


for image_path in all_images:

    filename = os.path.basename(
        image_path
    ).lower()

    folder_path = image_path.lower()


    # Tomato
    if "tomato" in folder_path:

        plant_images[
            "Tomato"
        ].append(
            image_path
        )


    # Potato
    elif "potato" in folder_path:

        plant_images[
            "Potato"
        ].append(
            image_path
        )


    # Bell Pepper
    elif (
        "pepper" in folder_path
        or "bell" in filename
    ):

        plant_images[
            "Bell_Pepper"
        ].append(
            image_path
        )


# ============================================================
# COPY IMAGES
# ============================================================

for plant, images in plant_images.items():

    random.shuffle(
        images
    )

    selected_images = images[
        :SAMPLES_PER_PLANT
    ]

    destination = os.path.join(
        OUTPUT_DIR,
        plant
    )

    print(
        f"{plant}: "
        f"{len(images)} available → "
        f"{len(selected_images)} selected"
    )

    for index, image_path in enumerate(
        selected_images
    ):

        extension = os.path.splitext(
            image_path
        )[1]

        new_filename = (
            f"{plant}_{index}"
            f"{extension}"
        )

        destination_path = os.path.join(
            destination,
            new_filename
        )

        shutil.copy2(
            image_path,
            destination_path
        )


# ============================================================
# SUMMARY
# ============================================================

print("\n================================")
print("Validator dataset created!")
print("================================")

for plant in classes:

    folder = os.path.join(
        OUTPUT_DIR,
        plant
    )

    count = len(
        os.listdir(folder)
    )

    print(
        f"{plant}: {count} images"
    )

print(
    "\nIMPORTANT:"
)

print(
    "The 'Other' class will be added "
    "separately using non-supported plants."
)