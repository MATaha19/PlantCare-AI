import os
import json

import cv2
import numpy as np
import tensorflow as tf
from PIL import Image


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ============================================================
# MODEL PATHS
# ============================================================

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
# CONFIGURATION
# ============================================================

IMAGE_SIZE = (
    224,
    224
)

SUPPORTED_PLANTS = [
    "Tomato",
    "Potato",
    "Bell Pepper"
]

SUPPORTED_CLASSES = {
    "Tomato",
    "Potato",
    "Bell_Pepper"
}

OTHER_CLASS = "Other"


# ============================================================
# CONFIDENCE THRESHOLDS
# ============================================================

STRONG_CONFIDENCE = 70.0

MIN_SUPPORTED_CONFIDENCE = 45.0

MIN_DISEASE_TOLERANT_CONFIDENCE = 20.0


# ============================================================
# LOAD CLASS NAMES
# ============================================================

if not os.path.exists(
    CLASS_NAMES_PATH
):

    raise FileNotFoundError(
        "Validator class file not found: "
        f"{CLASS_NAMES_PATH}"
    )


with open(
    CLASS_NAMES_PATH,
    "r"
) as file:

    VALIDATOR_CLASSES = json.load(
        file
    )


print(
    "Validator classes:",
    VALIDATOR_CLASSES
)


# ============================================================
# LOAD MODEL
# ============================================================

if not os.path.exists(
    MODEL_PATH
):

    raise FileNotFoundError(
        "Validator model not found: "
        f"{MODEL_PATH}"
    )


print(
    "Loading PlantCare AI plant validator..."
)


validator_model = tf.keras.models.load_model(
    MODEL_PATH
)


print(
    "Plant validator loaded successfully."
)


# ============================================================
# FORMAT PLANT NAME
# ============================================================

def format_plant_name(
    class_name
):

    names = {
        "Tomato": "Tomato",
        "Potato": "Potato",
        "Bell_Pepper": "Bell Pepper",
        "Other": "Other"
    }

    return names.get(
        class_name,
        class_name
    )


# ============================================================
# IMAGE CONVERSION
# ============================================================

def _convert_to_rgb(
    image
):
    """
    Convert supported image formats into RGB NumPy array.
    """

    if isinstance(
        image,
        Image.Image
    ):

        return np.array(
            image.convert("RGB")
        )


    if isinstance(
        image,
        np.ndarray
    ):

        array = image.copy()


        if array.ndim == 2:

            return cv2.cvtColor(
                array,
                cv2.COLOR_GRAY2RGB
            )


        if array.ndim != 3:

            raise ValueError(
                "Invalid image dimensions."
            )


        if array.shape[2] == 4:

            return cv2.cvtColor(
                array,
                cv2.COLOR_RGBA2RGB
            )


        if array.shape[2] != 3:

            raise ValueError(
                "Image must contain 3 or 4 channels."
            )


        return array


    raise TypeError(
        "Unsupported image type."
    )


# ============================================================
# VEGETATION CHECK
# ============================================================

def vegetation_check(
    image
):
    """
    Perform a tolerant visual leaf check.

    This check is intentionally not a strict green detector.
    Diseased leaves can be yellow, brown, dark, or reddish.
    """

    try:

        image_rgb = _convert_to_rgb(
            image
        )

    except Exception:

        return {
            "valid": False,
            "reason": "Invalid image",
            "visual_score": 0.0,
            "green_ratio": 0.0,
            "leaf_ratio": 0.0
        }


    image_rgb = cv2.resize(
        image_rgb,
        IMAGE_SIZE,
        interpolation=cv2.INTER_AREA
    )


    hsv = cv2.cvtColor(
        image_rgb,
        cv2.COLOR_RGB2HSV
    )


    h = hsv[:, :, 0]

    s = hsv[:, :, 1]

    v = hsv[:, :, 2]


    # --------------------------------------------------------
    # Green
    # --------------------------------------------------------

    green_mask = (
        (h >= 20)
        &
        (h <= 100)
        &
        (s >= 20)
        &
        (v >= 25)
    )


    # --------------------------------------------------------
    # Yellow
    # --------------------------------------------------------

    yellow_mask = (
        (h >= 12)
        &
        (h <= 50)
        &
        (s >= 25)
        &
        (v >= 40)
    )


    # --------------------------------------------------------
    # Red / Brown
    # --------------------------------------------------------

    red_brown_mask = (
        (
            (h <= 20)
            |
            (h >= 160)
        )
        &
        (s >= 25)
        &
        (v >= 20)
    )


    # --------------------------------------------------------
    # Dark organic tissue
    # --------------------------------------------------------

    dark_leaf_mask = (
        (v >= 20)
        &
        (v <= 150)
        &
        (s >= 20)
    )


    # --------------------------------------------------------
    # Combined mask
    # --------------------------------------------------------

    leaf_mask = (
        green_mask
        |
        yellow_mask
        |
        red_brown_mask
        |
        dark_leaf_mask
    )


    leaf_mask = (
        leaf_mask
        &
        (v >= 20)
    )


    # --------------------------------------------------------
    # Morphological cleanup
    # --------------------------------------------------------

    mask_uint8 = (
        leaf_mask.astype(
            np.uint8
        )
        *
        255
    )


    kernel = np.ones(
        (5, 5),
        np.uint8
    )


    mask_uint8 = cv2.morphologyEx(
        mask_uint8,
        cv2.MORPH_OPEN,
        kernel
    )


    mask_uint8 = cv2.morphologyEx(
        mask_uint8,
        cv2.MORPH_CLOSE,
        kernel
    )


    # --------------------------------------------------------
    # Ratios
    # --------------------------------------------------------

    total_pixels = (
        mask_uint8.shape[0]
        *
        mask_uint8.shape[1]
    )


    leaf_pixels = np.count_nonzero(
        mask_uint8
    )


    leaf_ratio = (
        leaf_pixels
        /
        float(total_pixels)
    )


    green_pixels = np.count_nonzero(
        green_mask
    )


    green_ratio = (
        green_pixels
        /
        float(total_pixels)
    )


    yellow_pixels = np.count_nonzero(
        yellow_mask
    )


    yellow_ratio = (
        yellow_pixels
        /
        float(total_pixels)
    )


    damaged_pixels = np.count_nonzero(
        red_brown_mask
    )


    damaged_ratio = (
        damaged_pixels
        /
        float(total_pixels)
    )


    # --------------------------------------------------------
    # Contours
    # --------------------------------------------------------

    contours, _ = cv2.findContours(
        mask_uint8,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )


    largest_area_ratio = 0.0

    aspect_ratio = 1.0


    if contours:

        largest_contour = max(
            contours,
            key=cv2.contourArea
        )


        largest_area = cv2.contourArea(
            largest_contour
        )


        image_area = (
            mask_uint8.shape[0]
            *
            mask_uint8.shape[1]
        )


        largest_area_ratio = (
            largest_area
            /
            float(image_area)
        )


        x, y, width, height = (
            cv2.boundingRect(
                largest_contour
            )
        )


        if height > 0:

            aspect_ratio = (
                width
                /
                float(height)
            )


    # --------------------------------------------------------
    # Texture
    # --------------------------------------------------------

    gray = cv2.cvtColor(
        image_rgb,
        cv2.COLOR_RGB2GRAY
    )


    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )


    edges = cv2.Canny(
        blurred,
        40,
        120
    )


    edge_ratio = float(
        np.mean(
            edges > 0
        )
    )


    # --------------------------------------------------------
    # Visual score
    # --------------------------------------------------------

    coverage_score = min(
        leaf_ratio / 0.50,
        1.0
    )


    contour_score = min(
        largest_area_ratio / 0.30,
        1.0
    )


    shape_score = (
        1.0
        if 0.15 <= aspect_ratio <= 6.0
        else 0.4
    )


    texture_score = min(
        edge_ratio / 0.20,
        1.0
    )


    color_score = min(
        (
            green_ratio
            +
            yellow_ratio
            +
            damaged_ratio
        )
        /
        0.50,
        1.0
    )


    visual_score = (
        coverage_score * 0.40
        +
        contour_score * 0.25
        +
        shape_score * 0.15
        +
        texture_score * 0.10
        +
        color_score * 0.10
    )


    visual_score = float(
        np.clip(
            visual_score,
            0.0,
            1.0
        )
    )


    # --------------------------------------------------------
    # Decision
    # --------------------------------------------------------

    valid = (
        visual_score >= 0.18
        or
        leaf_ratio >= 0.08
    )


    if valid:

        reason = (
            "Leaf-like visual evidence detected"
        )

    else:

        reason = (
            "Insufficient leaf-like visual evidence"
        )


    return {
        "valid": bool(valid),
        "reason": reason,
        "visual_score": round(
            visual_score,
            4
        ),
        "green_ratio": round(
            green_ratio * 100,
            2
        ),
        "leaf_ratio": round(
            leaf_ratio * 100,
            2
        )
    }


# ============================================================
# MODEL INPUT
# ============================================================

def _prepare_model_input(
    image
):
    """
    Prepare image for the NEW validator model.

    IMPORTANT:
    The model itself contains the MobileNetV2-compatible
    [-1, +1] Rescaling layer.

    Therefore we MUST NOT divide by 255 here.
    """

    image_rgb = _convert_to_rgb(
        image
    )


    image_rgb = cv2.resize(
        image_rgb,
        IMAGE_SIZE,
        interpolation=cv2.INTER_AREA
    )


    image_array = image_rgb.astype(
        np.float32
    )


    # IMPORTANT:
    # Do NOT normalize here.
    #
    # The model performs:
    #
    # x / 127.5 - 1
    #
    # internally.


    image_array = np.expand_dims(
        image_array,
        axis=0
    )


    return image_array


# ============================================================
# PREDICT PLANT
# ============================================================

def _predict_plant(
    image
):

    model_input = _prepare_model_input(
        image
    )


    prediction = validator_model.predict(
        model_input,
        verbose=0
    )


    prediction = np.asarray(
        prediction,
        dtype=np.float32
    )


    prediction = prediction.flatten()


    if len(prediction) != len(
        VALIDATOR_CLASSES
    ):

        raise ValueError(
            "Validator model output count does not match "
            "plant_validator_classes.json. "
            f"Model output: {len(prediction)}, "
            f"Class names: {len(VALIDATOR_CLASSES)}."
        )


    predicted_index = int(
        np.argmax(
            prediction
        )
    )


    predicted_class = (
        VALIDATOR_CLASSES[
            predicted_index
        ]
    )


    confidence = (
        float(
            prediction[
                predicted_index
            ]
        )
        *
        100.0
    )


    top_indices = np.argsort(
        prediction
    )[::-1]


    top_predictions = []


    for index in top_indices[:3]:

        top_predictions.append(
            {
                "class": VALIDATOR_CLASSES[
                    int(index)
                ],
                "confidence": round(
                    float(
                        prediction[
                            index
                        ]
                    )
                    *
                    100.0,
                    2
                )
            }
        )


    return (
        predicted_class,
        confidence,
        prediction,
        top_predictions
    )


# ============================================================
# PUBLIC VALIDATION FUNCTION
# ============================================================

def validate_plant_image(
    image
):

    # ========================================================
    # IMAGE EXISTENCE
    # ========================================================

    if image is None:

        return {
            "valid": False,
            "plant": "Unknown",
            "confidence": 0.0,
            "visual_score": 0.0,
            "reason": "No image supplied",
            "message": "No image was provided."
        }


    # ========================================================
    # BASIC IMAGE VALIDATION
    # ========================================================

    try:

        image_rgb = _convert_to_rgb(
            image
        )

    except Exception as error:

        return {
            "valid": False,
            "plant": "Unknown",
            "confidence": 0.0,
            "visual_score": 0.0,
            "reason": "Invalid image",
            "message": (
                "Unable to process the uploaded image: "
                f"{error}"
            )
        }


    if image_rgb.ndim != 3:

        return {
            "valid": False,
            "plant": "Unknown",
            "confidence": 0.0,
            "visual_score": 0.0,
            "reason": "Invalid image dimensions",
            "message": (
                "The uploaded image has invalid dimensions."
            )
        }


    height, width = (
        image_rgb.shape[:2]
    )


    if height < 50 or width < 50:

        return {
            "valid": False,
            "plant": "Unknown",
            "confidence": 0.0,
            "visual_score": 0.0,
            "reason": "Image too small",
            "message": (
                "Please upload a larger plant leaf image."
            )
        }


    # ========================================================
    # VISUAL CHECK
    # ========================================================

    visual_result = vegetation_check(
        image_rgb
    )


    visual_score = float(
        visual_result.get(
            "visual_score",
            0.0
        )
    )


    # ========================================================
    # CNN VALIDATOR
    # ========================================================

    try:

        (
            predicted_class,
            confidence,
            prediction,
            top_predictions
        ) = _predict_plant(
            image_rgb
        )

    except Exception as error:

        return {
            "valid": False,
            "plant": "Unknown",
            "confidence": 0.0,
            "visual_score": visual_score,
            "reason": "Plant classifier error",
            "message": (
                "Plant validation failed: "
                f"{error}"
            )
        }


    formatted_plant = format_plant_name(
        predicted_class
    )


    # ========================================================
    # OTHER
    # ========================================================

    if predicted_class == OTHER_CLASS:

        supported_predictions = []

        for item in top_predictions:

            if item["class"] in SUPPORTED_CLASSES:

                supported_predictions.append(
                    item
                )


        if supported_predictions:

            best_supported = (
                supported_predictions[0]
            )


            best_supported_confidence = float(
                best_supported["confidence"]
            )


            if (
                best_supported_confidence
                >= MIN_DISEASE_TOLERANT_CONFIDENCE
                and
                visual_score >= 0.35
            ):

                supported_class = (
                    best_supported["class"]
                )


                supported_plant = (
                    format_plant_name(
                        supported_class
                    )
                )


                return {
                    "valid": True,
                    "plant": supported_plant,
                    "confidence": round(
                        best_supported_confidence,
                        2
                    ),
                    "visual_score": round(
                        visual_score,
                        4
                    ),
                    "reason": (
                        "Strong leaf evidence with "
                        "uncertain plant classification"
                    ),
                    "message": (
                        f"The image appears to contain a "
                        f"supported plant leaf, most likely "
                        f"{supported_plant}."
                    )
                }


        return {
            "valid": False,
            "plant": "Unknown",
            "confidence": round(
                confidence,
                2
            ),
            "visual_score": round(
                visual_score,
                4
            ),
            "reason": (
                "Validator classified image as Other"
            ),
            "message": (
                "The plant validator could not identify "
                "the image as Tomato, Potato, or Bell Pepper."
            )
        }


    # ========================================================
    # STRONG SUPPORTED PLANT
    # ========================================================

    if (
        predicted_class in SUPPORTED_CLASSES
        and
        confidence >= STRONG_CONFIDENCE
    ):

        return {
            "valid": True,
            "plant": formatted_plant,
            "confidence": round(
                confidence,
                2
            ),
            "visual_score": round(
                visual_score,
                4
            ),
            "reason": (
                "Strong supported-plant classification"
            ),
            "message": (
                f"The image was identified as a "
                f"{formatted_plant} leaf."
            )
        }


    # ========================================================
    # MODERATE CONFIDENCE
    # ========================================================

    if (
        predicted_class in SUPPORTED_CLASSES
        and
        confidence >= MIN_SUPPORTED_CONFIDENCE
    ):

        return {
            "valid": True,
            "plant": formatted_plant,
            "confidence": round(
                confidence,
                2
            ),
            "visual_score": round(
                visual_score,
                4
            ),
            "reason": (
                "Supported plant with moderate confidence"
            ),
            "message": (
                f"The image appears to contain a "
                f"{formatted_plant} leaf."
            )
        }


    # ========================================================
    # DISEASE-TOLERANT VALIDATION
    # ========================================================

    if (
        predicted_class in SUPPORTED_CLASSES
        and
        confidence >= MIN_DISEASE_TOLERANT_CONFIDENCE
        and
        visual_score >= 0.30
    ):

        return {
            "valid": True,
            "plant": formatted_plant,
            "confidence": round(
                confidence,
                2
            ),
            "visual_score": round(
                visual_score,
                4
            ),
            "reason": (
                "Disease-tolerant validation"
            ),
            "message": (
                f"The validator identified the image as "
                f"{formatted_plant} with lower confidence, "
                "but sufficient leaf-like visual evidence "
                "was detected."
            )
        }


    # ========================================================
    # FINAL REJECTION
    # ========================================================

    return {
        "valid": False,
        "plant": "Unknown",
        "confidence": round(
            confidence,
            2
        ),
        "visual_score": round(
            visual_score,
            4
        ),
        "reason": (
            "Insufficient supported-plant evidence"
        ),
        "message": (
            "The uploaded image could not be reliably "
            "identified as Tomato, Potato, or Bell Pepper."
        )
    }


# ============================================================
# SIMPLE BOOLEAN HELPER
# ============================================================

def is_supported_plant(
    image
):

    result = validate_plant_image(
        image
    )

    return bool(
        result["valid"]
    )