import os
import shutil
import random


# ============================================================
# CONFIGURATION
# ============================================================

PLANTDOC_DIR = r"C:\Users\Mohammed Taha\Downloads\PlantDoc-Dataset-master"

OUTPUT_DIR = "validator_dataset"

OTHER_DIR = os.path.join(
    OUTPUT_DIR,
    "Other"
)

MAX_PER_SPECIES = 250

SUPPORTED_KEYWORDS = [
    "tomato",
    "potato",
    "pepper",
    "bell pepper"
]

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".JPG",
    ".JPEG",
    ".PNG"
)


# ============================================================
# CHECK OUTPUT PATH
# ============================================================

if os.path.exists(OTHER_DIR):

    if not os.path.isdir(OTHER_DIR):

        print(
            "ERROR: validator_dataset\\Other exists "
            "but it is NOT a folder."
        )

        print(
            "Please remove that file and create an "
            "Other folder."
        )

        raise SystemExit(1)

else:

    os.makedirs(
        OTHER_DIR
    )


# ============================================================
# FIND ALL IMAGES
# ============================================================

all_images = []

for split in ["train", "test"]:

    split_path = os.path.join(
        PLANTDOC_DIR,
        split
    )

    if not os.path.isdir(split_path):

        print(
            f"Warning: {split_path} does not exist."
        )

        continue

    for root, dirs, files in os.walk(
        split_path
    ):

        for file in files:

            if file.endswith(
                IMAGE_EXTENSIONS
            ):

                all_images.append(
                    os.path.join(
                        root,
                        file
                    )
                )


print()
print("=" * 60)
print("PLANTDOC SCAN")
print("=" * 60)

print(
    f"Total images found: {len(all_images)}"
)


# ============================================================
# GROUP IMAGES BY PLANT CATEGORY
# ============================================================

plant_groups = {}


for image_path in all_images:

    parent_folder = os.path.basename(
        os.path.dirname(image_path)
    )

    category = parent_folder.strip()

    if not category:
        continue

    category_lower = category.lower()


    # --------------------------------------------------------
    # EXCLUDE SUPPORTED PLANTS
    # --------------------------------------------------------

    is_supported = any(
        keyword in category_lower
        for keyword in SUPPORTED_KEYWORDS
    )

    if is_supported:
        continue


    # --------------------------------------------------------
    # ADD TO OTHER
    # --------------------------------------------------------

    if category not in plant_groups:

        plant_groups[category] = []

    plant_groups[
        category
    ].append(
        image_path
    )


# ============================================================
# DISPLAY CATEGORIES
# ============================================================

print()
print("Unsupported plant categories found:")
print("-" * 60)

for category, images in sorted(
    plant_groups.items()
):

    print(
        f"{category}: {len(images)} images"
    )


# ============================================================
# COPY IMAGES
# ============================================================

print()
print("=" * 60)
print("CREATING OTHER DATASET")
print("=" * 60)


total_copied = 0


for category, images in sorted(
    plant_groups.items()
):

    random.shuffle(
        images
    )

    selected = images[
        :MAX_PER_SPECIES
    ]


    safe_category = "".join(
        character
        if character.isalnum()
        else "_"
        for character in category
    )


    print(
        f"{category}: copying "
        f"{len(selected)} images"
    )


    for index, image_path in enumerate(
        selected
    ):

        extension = os.path.splitext(
            image_path
        )[1]


        filename = (
            f"{safe_category}_"
            f"{index}"
            f"{extension}"
        )


        destination = os.path.join(
            OTHER_DIR,
            filename
        )


        if os.path.exists(
            destination
        ):

            continue


        shutil.copy2(
            image_path,
            destination
        )

        total_copied += 1


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 60)
print("DONE")
print("=" * 60)

print(
    f"Total Other images copied: "
    f"{total_copied}"
)

print()
print(
    "Output:"
)

print(
    os.path.abspath(
        OTHER_DIR
    )
)


# ============================================================
# DATASET COUNTS
# ============================================================

print()
print("Validator dataset:")

for folder in [
    "Tomato",
    "Potato",
    "Bell_Pepper",
    "Other"
]:

    path = os.path.join(
        OUTPUT_DIR,
        folder
    )

    if not os.path.isdir(path):
        count = 0

    else:

        count = len([
            file
            for file in os.listdir(path)
            if file.endswith(
                IMAGE_EXTENSIONS
            )
        ])

    print(
        f"{folder}: {count} images"
    )