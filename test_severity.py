import cv2
import numpy as np


def analyze_severity(image):
    """
    Estimate possible affected regions on a plant leaf.

    Returns:
        affected_percentage
        severity_level
        highlighted_image
    """

    # ------------------------------------------
    # Convert RGB image to OpenCV format
    # ------------------------------------------

    image = np.array(image)

    image = cv2.cvtColor(
        image,
        cv2.COLOR_RGB2BGR
    )

    # ------------------------------------------
    # Resize
    # ------------------------------------------

    image = cv2.resize(
        image,
        (224, 224)
    )

    original = image.copy()

    # ------------------------------------------
    # Convert to HSV
    # ------------------------------------------

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    # ------------------------------------------
    # Leaf detection
    # ------------------------------------------

    lower_green = np.array(
        [20, 20, 20]
    )

    upper_green = np.array(
        [100, 255, 255]
    )

    leaf_mask = cv2.inRange(
        hsv,
        lower_green,
        upper_green
    )

    # ------------------------------------------
    # Detect possible disease discoloration
    # ------------------------------------------

    lower_brown = np.array(
        [5, 30, 20]
    )

    upper_brown = np.array(
        [35, 255, 230]
    )

    disease_mask = cv2.inRange(
        hsv,
        lower_brown,
        upper_brown
    )

    # Also detect very dark regions
    lower_dark = np.array(
        [0, 0, 0]
    )

    upper_dark = np.array(
        [180, 255, 80]
    )

    dark_mask = cv2.inRange(
        hsv,
        lower_dark,
        upper_dark
    )

    # Combine possible affected regions
    possible_affected = cv2.bitwise_or(
        disease_mask,
        dark_mask
    )

    # Restrict to leaf
    affected_mask = cv2.bitwise_and(
        possible_affected,
        leaf_mask
    )

    # ------------------------------------------
    # Remove tiny noise
    # ------------------------------------------

    kernel = np.ones(
        (5, 5),
        np.uint8
    )

    affected_mask = cv2.morphologyEx(
        affected_mask,
        cv2.MORPH_OPEN,
        kernel
    )

    affected_mask = cv2.morphologyEx(
        affected_mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    # ------------------------------------------
    # Calculate affected percentage
    # ------------------------------------------

    leaf_pixels = np.count_nonzero(
        leaf_mask
    )

    affected_pixels = np.count_nonzero(
        affected_mask
    )

    if leaf_pixels == 0:

        affected_percentage = 0.0

    else:

        affected_percentage = (
            affected_pixels /
            leaf_pixels
        ) * 100

    affected_percentage = min(
        affected_percentage,
        100
    )

    # ------------------------------------------
    # Severity classification
    # ------------------------------------------

    if affected_percentage < 10:

        severity_level = "Mild"

    elif affected_percentage < 30:

        severity_level = "Moderate"

    else:

        severity_level = "Severe"

    # ------------------------------------------
    # Create RED overlay
    # ------------------------------------------

    overlay = original.copy()

    # BGR = Red
    overlay[affected_mask > 0] = (
        0,
        0,
        255
    )

    # Blend overlay with original
    highlighted = cv2.addWeighted(
        original,
        0.65,
        overlay,
        0.35,
        0
    )

    # Draw contours around detected regions
    contours, _ = cv2.findContours(
        affected_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    cv2.drawContours(
        highlighted,
        contours,
        -1,
        (0, 0, 255),
        2
    )

    # Convert back to RGB
    highlighted = cv2.cvtColor(
        highlighted,
        cv2.COLOR_BGR2RGB
    )

    return (
        affected_percentage,
        severity_level,
        highlighted
    )