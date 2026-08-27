import cv2
import numpy as np
from PIL import Image


# ============================================================
# SEVERITY ANALYSIS
# ============================================================
#
# This module estimates visible diseased/discolored area
# relative to the detected leaf area.
#
# IMPORTANT:
# This is an image-processing screening estimate.
# It is NOT a laboratory measurement.
#
# Pipeline:
#
# 1. Convert input image to OpenCV format
# 2. Resize for efficient processing
# 3. Detect the leaf / foreground
# 4. Clean the leaf mask
# 5. Estimate healthy leaf color
# 6. Detect abnormal/discolored regions
# 7. Remove tiny noise
# 8. Restrict disease mask to leaf mask
# 9. Calculate affected area relative to leaf area
# 10. Generate highlighted visualization
#
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

MAX_PROCESSING_SIZE = 900

MIN_LEAF_AREA_RATIO = 0.05

MIN_COMPONENT_AREA = 20

MORPH_KERNEL_SMALL = 3
MORPH_KERNEL_MEDIUM = 5

# Severity thresholds are based on visible affected
# leaf area, NOT the complete image.
#
# 0 - 5%       -> Mild
# >5 - 15%     -> Moderate
# >15%          -> Severe

MILD_THRESHOLD = 5.0
MODERATE_THRESHOLD = 15.0


# ============================================================
# IMAGE CONVERSION
# ============================================================

def _to_bgr(image):
    """
    Convert PIL / NumPy image into OpenCV BGR format.
    """

    if isinstance(image, Image.Image):

        rgb = np.array(
            image.convert("RGB")
        )

        return cv2.cvtColor(
            rgb,
            cv2.COLOR_RGB2BGR
        )

    if isinstance(image, np.ndarray):

        array = image.copy()

        if array.ndim == 2:

            return cv2.cvtColor(
                array,
                cv2.COLOR_GRAY2BGR
            )

        if array.shape[2] == 4:

            return cv2.cvtColor(
                array,
                cv2.COLOR_RGBA2BGR
            )

        return array

    raise TypeError(
        "Unsupported image type. "
        "Expected PIL Image or NumPy array."
    )


# ============================================================
# RESIZE IMAGE
# ============================================================

def _resize_for_processing(image):
    """
    Resize large images while preserving aspect ratio.
    """

    height, width = image.shape[:2]

    largest_dimension = max(
        height,
        width
    )

    if largest_dimension <= MAX_PROCESSING_SIZE:

        return image

    scale = (
        MAX_PROCESSING_SIZE /
        float(largest_dimension)
    )

    new_width = max(
        1,
        int(width * scale)
    )

    new_height = max(
        1,
        int(height * scale)
    )

    return cv2.resize(
        image,
        (new_width, new_height),
        interpolation=cv2.INTER_AREA
    )


# ============================================================
# MORPHOLOGICAL CLEANING
# ============================================================

def _clean_mask(mask):
    """
    Remove small isolated noise and fill small gaps.
    """

    kernel_small = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (
            MORPH_KERNEL_SMALL,
            MORPH_KERNEL_SMALL
        )
    )

    kernel_medium = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (
            MORPH_KERNEL_MEDIUM,
            MORPH_KERNEL_MEDIUM
        )
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel_small
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel_medium
    )

    return mask


# ============================================================
# KEEP SIGNIFICANT COMPONENTS
# ============================================================

def _remove_small_components(
    mask,
    minimum_area=MIN_COMPONENT_AREA
):
    """
    Remove tiny connected components.
    """

    binary = (
        mask > 0
    ).astype(
        np.uint8
    )

    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        binary,
        connectivity=8
    )

    cleaned = np.zeros_like(
        binary,
        dtype=np.uint8
    )

    for component_index in range(
        1,
        count
    ):

        area = stats[
            component_index,
            cv2.CC_STAT_AREA
        ]

        if area >= minimum_area:

            cleaned[
                labels == component_index
            ] = 255

    return cleaned


# ============================================================
# LEAF MASK — COLOR SEGMENTATION
# ============================================================

def _color_leaf_mask(image):
    """
    Estimate leaf pixels using multiple color cues.

    Green is the strongest cue, but the method also keeps
    non-green foreground regions so severely diseased leaves
    are not automatically discarded.
    """

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB
    )

    b, g, r = cv2.split(
        image
    )

    h, s, v = cv2.split(
        hsv
    )

    # --------------------------------------------------------
    # Excess Green
    # --------------------------------------------------------

    exg = (
        2.0 * g.astype(np.float32)
        - r.astype(np.float32)
        - b.astype(np.float32)
    )

    green_mask = (
        (exg > 10)
        & (g >= r * 0.85)
        & (g >= b * 0.80)
        & (s > 25)
        & (v > 35)
    )

    # --------------------------------------------------------
    # Green HSV
    # --------------------------------------------------------

    hsv_green = (
        (h >= 25)
        & (h <= 100)
        & (s >= 25)
        & (v >= 30)
    )

    # --------------------------------------------------------
    # Yellow / chlorotic leaf regions
    #
    # Important for severely diseased leaves.
    # --------------------------------------------------------

    yellow_leaf = (
        (h >= 15)
        & (h <= 45)
        & (s >= 35)
        & (v >= 70)
    )

    # --------------------------------------------------------
    # Brown / reddish leaf regions
    #
    # Important for blight and bacterial spots.
    # --------------------------------------------------------

    brown_leaf = (
        (
            (h <= 25)
            | (h >= 160)
        )
        & (s >= 35)
        & (v >= 25)
        & (v <= 220)
    )

    # --------------------------------------------------------
    # Non-background foreground candidate
    #
    # Useful when severe disease changes most of the leaf
    # away from green.
    # --------------------------------------------------------

    non_background = (
        (s > 25)
        & (v > 30)
    )

    color_mask = (
        green_mask
        | hsv_green
        | yellow_leaf
        | brown_leaf
    )

    color_mask = (
        color_mask
        & non_background
    )

    return (
        color_mask.astype(
            np.uint8
        ) * 255
    )


# ============================================================
# GRABCUT FOREGROUND MASK
# ============================================================

def _grabcut_leaf_mask(image):
    """
    Use GrabCut as a secondary foreground estimator.

    This helps when severe disease changes the normal green
    appearance of the leaf.
    """

    height, width = image.shape[:2]

    if height < 20 or width < 20:

        return np.zeros(
            (height, width),
            dtype=np.uint8
        )

    # Conservative border rectangle.
    margin_x = max(
        2,
        int(width * 0.03)
    )

    margin_y = max(
        2,
        int(height * 0.03)
    )

    rect_width = max(
        1,
        width - (2 * margin_x)
    )

    rect_height = max(
        1,
        height - (2 * margin_y)
    )

    mask = np.zeros(
        (height, width),
        np.uint8
    )

    bgd_model = np.zeros(
        (1, 65),
        np.float64
    )

    fgd_model = np.zeros(
        (1, 65),
        np.float64
    )

    try:

        cv2.grabCut(
            image,
            mask,
            (
                margin_x,
                margin_y,
                rect_width,
                rect_height
            ),
            bgd_model,
            fgd_model,
            3,
            cv2.GC_INIT_WITH_RECT
        )

    except Exception:

        return np.zeros(
            (height, width),
            dtype=np.uint8
        )

    foreground = (
        (mask == cv2.GC_FGD)
        | (mask == cv2.GC_PR_FGD)
    )

    return (
        foreground.astype(
            np.uint8
        ) * 255
    )


# ============================================================
# LARGEST COMPONENT
# ============================================================

def _largest_component(mask):
    """
    Keep the largest connected foreground object.

    A leaf is normally the dominant object in the image.
    """

    binary = (
        mask > 0
    ).astype(
        np.uint8
    )

    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        binary,
        connectivity=8
    )

    if count <= 1:

        return np.zeros_like(
            mask,
            dtype=np.uint8
        )

    largest_index = 1
    largest_area = stats[
        1,
        cv2.CC_STAT_AREA
    ]

    for index in range(
        2,
        count
    ):

        area = stats[
            index,
            cv2.CC_STAT_AREA
        ]

        if area > largest_area:

            largest_area = area
            largest_index = index

    result = np.zeros_like(
        mask,
        dtype=np.uint8
    )

    result[
        labels == largest_index
    ] = 255

    return result


# ============================================================
# LEAF MASK
# ============================================================

def _detect_leaf_mask(image):
    """
    Build a robust leaf mask using both color segmentation
    and GrabCut.

    The two masks are combined carefully so that a severely
    diseased leaf is not rejected simply because it is no
    longer strongly green.
    """

    height, width = image.shape[:2]

    image_area = (
        height * width
    )

    color_mask = _color_leaf_mask(
        image
    )

    color_mask = _clean_mask(
        color_mask
    )

    grabcut_mask = _grabcut_leaf_mask(
        image
    )

    grabcut_mask = _clean_mask(
        grabcut_mask
    )

    color_area = cv2.countNonZero(
        color_mask
    )

    grabcut_area = cv2.countNonZero(
        grabcut_mask
    )

    # --------------------------------------------------------
    # Prefer the color mask when it has a reasonable amount
    # of plant-like pixels.
    # --------------------------------------------------------

    color_ratio = (
        color_area /
        float(image_area)
    )

    grabcut_ratio = (
        grabcut_area /
        float(image_area)
    )

    if color_ratio >= MIN_LEAF_AREA_RATIO:

        combined = cv2.bitwise_or(
            color_mask,
            grabcut_mask
        )

    elif grabcut_ratio >= MIN_LEAF_AREA_RATIO:

        combined = grabcut_mask

    else:

        combined = cv2.bitwise_or(
            color_mask,
            grabcut_mask
        )

    combined = _clean_mask(
        combined
    )

    # --------------------------------------------------------
    # Keep the dominant connected region.
    # --------------------------------------------------------

    largest = _largest_component(
        combined
    )

    largest_area = cv2.countNonZero(
        largest
    )

    # If largest component is clearly useful, use it.
    if largest_area >= (
        image_area *
        MIN_LEAF_AREA_RATIO
    ):

        leaf_mask = largest

    else:

        leaf_mask = combined

    # --------------------------------------------------------
    # Final smoothing.
    # --------------------------------------------------------

    leaf_mask = _clean_mask(
        leaf_mask
    )

    return leaf_mask


# ============================================================
# HEALTHY COLOR ESTIMATION
# ============================================================

def _estimate_healthy_color(
    image,
    leaf_mask
):
    """
    Estimate the dominant healthy leaf color.

    We intentionally use the greener pixels rather than the
    average of the entire leaf because the entire leaf may
    already be diseased.
    """

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    h, s, v = cv2.split(
        hsv
    )

    b, g, r = cv2.split(
        image
    )

    leaf = (
        leaf_mask > 0
    )

    green_candidate = (
        leaf
        & (h >= 25)
        & (h <= 100)
        & (s >= 30)
        & (v >= 35)
        & (g.astype(np.int16) >= r.astype(np.int16) - 5)
    )

    pixels = image[
        green_candidate
    ]

    if len(pixels) < 50:

        pixels = image[
            leaf
        ]

    if len(pixels) == 0:

        return np.array(
            [0.0, 0.0, 0.0],
            dtype=np.float32
        )

    # Median is more resistant to lesions and shadows
    # than a simple mean.
    return np.median(
        pixels.astype(
            np.float32
        ),
        axis=0
    )


# ============================================================
# DISEASE / ABNORMAL COLOR MASK
# ============================================================

def _detect_disease_mask(
    image,
    leaf_mask
):
    """
    Detect visible abnormal/discolored areas inside the leaf.

    Multiple visual cues are combined:

    - Brown lesions
    - Dark lesions
    - Yellow/chlorotic regions
    - Red/brown discoloration
    - Strong deviation from dominant healthy leaf color

    The mask is always restricted to the leaf.
    """

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB
    )

    h, s, v = cv2.split(
        hsv
    )

    l_channel, a_channel, b_channel = cv2.split(
        lab
    )

    blue, green, red = cv2.split(
        image
    )

    leaf = (
        leaf_mask > 0
    )

    # --------------------------------------------------------
    # 1. Brown / reddish lesions
    # --------------------------------------------------------

    brown_mask = (
        leaf
        & (
            (
                (h <= 30)
                | (h >= 160)
            )
        )
        & (s >= 45)
        & (v >= 35)
        & (v <= 215)
    )

    # --------------------------------------------------------
    # 2. Yellow / chlorotic lesions
    # --------------------------------------------------------

    yellow_mask = (
        leaf
        & (h >= 15)
        & (h <= 45)
        & (s >= 45)
        & (v >= 80)
    )

    # --------------------------------------------------------
    # 3. Very dark lesions
    #
    # Do not count every dark pixel because veins and natural
    # shadows can also be dark.
    #
    # Require low brightness + sufficient saturation or
    # significant red/green/blue imbalance.
    # --------------------------------------------------------

    dark_mask = (
        leaf
        & (v < 70)
        & (
            (s > 45)
            | (
                np.abs(
                    red.astype(np.int16)
                    - green.astype(np.int16)
                ) > 18
            )
        )
    )

    # --------------------------------------------------------
    # 4. Pale / chlorotic tissue
    #
    # Low saturation + high brightness inside the leaf can
    # represent yellowing/fading tissue.
    # --------------------------------------------------------

    pale_mask = (
        leaf
        & (s < 55)
        & (v > 145)
        & (
            b_channel.astype(np.int16)
            > 125
        )
    )

    # --------------------------------------------------------
    # 5. Color deviation from dominant healthy leaf color
    # --------------------------------------------------------

    healthy_color = _estimate_healthy_color(
        image,
        leaf_mask
    )

    healthy_bgr = healthy_color

    color_distance = np.sqrt(
        (
            image[:, :, 0].astype(np.float32)
            - healthy_bgr[0]
        ) ** 2
        +
        (
            image[:, :, 1].astype(np.float32)
            - healthy_bgr[1]
        ) ** 2
        +
        (
            image[:, :, 2].astype(np.float32)
            - healthy_bgr[2]
        ) ** 2
    )

    # Adaptive threshold based on image variation.
    leaf_distances = color_distance[
        leaf
    ]

    if len(leaf_distances) > 100:

        median_distance = float(
            np.median(
                leaf_distances
            )
        )

        mad = float(
            np.median(
                np.abs(
                    leaf_distances
                    - median_distance
                )
            )
        )

        adaptive_threshold = max(
            28.0,
            median_distance
            + (2.8 * mad)
        )

        adaptive_threshold = min(
            adaptive_threshold,
            75.0
        )

    else:

        adaptive_threshold = 40.0

    deviation_mask = (
        leaf
        & (
            color_distance
            > adaptive_threshold
        )
        & (
            s > 25
        )
    )

    # --------------------------------------------------------
    # 6. Lab-space abnormality
    #
    # Lab makes color differences more stable than RGB.
    # --------------------------------------------------------

    leaf_lab_pixels = lab[
        leaf
    ]

    if len(leaf_lab_pixels) > 100:

        median_lab = np.median(
            leaf_lab_pixels.astype(
                np.float32
            ),
            axis=0
        )

        lab_distance = np.sqrt(
            (
                lab[:, :, 0].astype(
                    np.float32
                )
                - median_lab[0]
            ) ** 2
            +
            (
                lab[:, :, 1].astype(
                    np.float32
                )
                - median_lab[1]
            ) ** 2
            +
            (
                lab[:, :, 2].astype(
                    np.float32
                )
                - median_lab[2]
            ) ** 2
        )

        lab_mask = (
            leaf
            & (lab_distance > 22)
            & (s > 30)
        )

    else:

        lab_mask = np.zeros_like(
            leaf,
            dtype=bool
        )

    # --------------------------------------------------------
    # Combine strong disease indicators.
    #
    # Brown/yellow/dark regions are direct indicators.
    # Color/Lab deviation requires stronger evidence.
    # --------------------------------------------------------

    direct_mask = (
        brown_mask
        | yellow_mask
        | dark_mask
        | pale_mask
    )

    abnormal_mask = (
        direct_mask
        | (
            deviation_mask
            & lab_mask
        )
    )

    # Never allow pixels outside leaf.
    abnormal_mask = (
        abnormal_mask
        & leaf
    )

    disease_mask = (
        abnormal_mask.astype(
            np.uint8
        ) * 255
    )

    # --------------------------------------------------------
    # Remove tiny isolated spots.
    # --------------------------------------------------------

    disease_mask = _clean_mask(
        disease_mask
    )

    disease_mask = _remove_small_components(
        disease_mask,
        minimum_area=MIN_COMPONENT_AREA
    )

    # --------------------------------------------------------
    # Restrict again to leaf.
    # --------------------------------------------------------

    disease_mask = cv2.bitwise_and(
        disease_mask,
        leaf_mask
    )

    return disease_mask


# ============================================================
# EDGE-AWARE REFINEMENT
# ============================================================

def _refine_disease_mask(
    image,
    leaf_mask,
    disease_mask
):
    """
    Refine the disease mask while avoiding aggressive
    expansion across healthy leaf regions.
    """

    if cv2.countNonZero(
        disease_mask
    ) == 0:

        return disease_mask

    # Small closing fills holes inside lesions.
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3)
    )

    refined = cv2.morphologyEx(
        disease_mask,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=1
    )

    # Remove very small components after refinement.
    refined = _remove_small_components(
        refined,
        minimum_area=MIN_COMPONENT_AREA
    )

    # Restrict to leaf.
    refined = cv2.bitwise_and(
        refined,
        leaf_mask
    )

    return refined


# ============================================================
# SEVERITY CLASSIFICATION
# ============================================================

def _severity_from_percentage(
    affected_percentage
):
    """
    Convert affected-area percentage into a severity level.
    """

    if affected_percentage <= 0.5:

        return "No disease"

    if affected_percentage <= MILD_THRESHOLD:

        return "Mild"

    if affected_percentage <= MODERATE_THRESHOLD:

        return "Moderate"

    return "Severe"


# ============================================================
# HIGHLIGHT VISUALIZATION
# ============================================================

def _create_highlighted_image(
    image,
    leaf_mask,
    disease_mask
):
    """
    Create a visualization showing the detected affected
    regions over the original image.
    """

    result = image.copy()

    leaf = (
        leaf_mask > 0
    )

    disease = (
        disease_mask > 0
    )

    # --------------------------------------------------------
    # Slightly dim background so the leaf is easier to see.
    # --------------------------------------------------------

    background = ~leaf

    result[
        background
    ] = (
        result[
            background
        ].astype(
            np.float32
        ) * 0.45
    ).astype(
        np.uint8
    )

    # --------------------------------------------------------
    # Highlight detected affected regions.
    # --------------------------------------------------------

    if np.any(disease):

        overlay = result.copy()

        # Red highlight for affected tissue.
        overlay[disease] = (
            40,
            40,
            230
        )

        result = cv2.addWeighted(
            result,
            0.60,
            overlay,
            0.40,
            0
        )

        # Clear lesion boundary.
        contours, _ = cv2.findContours(
            disease_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        cv2.drawContours(
            result,
            contours,
            -1,
            (30, 30, 255),
            1
        )

    # --------------------------------------------------------
    # Convert BGR -> RGB for PIL / Streamlit.
    # --------------------------------------------------------

    rgb = cv2.cvtColor(
        result,
        cv2.COLOR_BGR2RGB
    )

    return Image.fromarray(
        rgb
    )


# ============================================================
# PUBLIC API
# ============================================================

def analyze_severity(image):
    """
    Analyze visible affected leaf area.

    Parameters
    ----------
    image:
        PIL Image or NumPy array.

    Returns
    -------
    affected_percentage:
        Float percentage of estimated affected leaf area.

    severity_level:
        One of:
            "No disease"
            "Mild"
            "Moderate"
            "Severe"

    highlighted_image:
        PIL Image showing detected affected regions.
    """

    # --------------------------------------------------------
    # Convert image.
    # --------------------------------------------------------

    bgr = _to_bgr(
        image
    )

    if bgr is None or bgr.size == 0:

        raise ValueError(
            "Invalid or empty image."
        )

    # --------------------------------------------------------
    # Normalize image size.
    # --------------------------------------------------------

    bgr = _resize_for_processing(
        bgr
    )

    # --------------------------------------------------------
    # Leaf segmentation.
    # --------------------------------------------------------

    leaf_mask = _detect_leaf_mask(
        bgr
    )

    leaf_area = cv2.countNonZero(
        leaf_mask
    )

    total_pixels = (
        bgr.shape[0]
        * bgr.shape[1]
    )

    # --------------------------------------------------------
    # Safety check.
    # --------------------------------------------------------

    if leaf_area < (
        total_pixels
        * MIN_LEAF_AREA_RATIO
    ):

        # We cannot reliably estimate severity when the
        # leaf itself could not be detected.
        #
        # Return an empty visualization rather than inventing
        # an affected percentage.
        highlighted_image = Image.fromarray(
            cv2.cvtColor(
                bgr,
                cv2.COLOR_BGR2RGB
            )
        )

        return (
            0.0,
            "Unknown",
            highlighted_image
        )

    # --------------------------------------------------------
    # Disease / abnormal tissue segmentation.
    # --------------------------------------------------------

    disease_mask = _detect_disease_mask(
        bgr,
        leaf_mask
    )

    disease_mask = _refine_disease_mask(
        bgr,
        leaf_mask,
        disease_mask
    )

    affected_pixels = cv2.countNonZero(
        disease_mask
    )

    # --------------------------------------------------------
    # CRITICAL CALCULATION
    #
    # Percentage is based ONLY on leaf pixels.
    #
    # NOT:
    #
    #     diseased_pixels / whole_image
    #
    # Instead:
    #
    #     diseased_pixels / leaf_pixels
    # --------------------------------------------------------

    affected_percentage = (
        affected_pixels /
        float(leaf_area)
    ) * 100.0

    # --------------------------------------------------------
    # Safety clamp.
    # --------------------------------------------------------

    affected_percentage = float(
        np.clip(
            affected_percentage,
            0.0,
            100.0
        )
    )

    # --------------------------------------------------------
    # Severity level.
    # --------------------------------------------------------

    severity_level = _severity_from_percentage(
        affected_percentage
    )

    # --------------------------------------------------------
    # Visualization.
    # --------------------------------------------------------

    highlighted_image = _create_highlighted_image(
        bgr,
        leaf_mask,
        disease_mask
    )

    return (
        round(
            affected_percentage,
            2
        ),
        severity_level,
        highlighted_image
    )