import numpy as np


# ============================================================
# VALIDATION SETTINGS
# ============================================================

MIN_CONFIDENCE = 70.0
MIN_MARGIN = 15.0


# ============================================================
# PREDICTION VALIDATION
# ============================================================

def validate_prediction(prediction):
    """
    Determine whether the CNN prediction is sufficiently
    confident and separated from the second-best prediction.

    Returns:
        is_valid
        reason
    """

    sorted_probabilities = np.sort(
        prediction
    )[::-1]

    top_confidence = (
        float(sorted_probabilities[0]) * 100
    )

    second_confidence = (
        float(sorted_probabilities[1]) * 100
    )

    margin = (
        top_confidence -
        second_confidence
    )

    # --------------------------------------------------------
    # Very low confidence
    # --------------------------------------------------------

    if top_confidence < MIN_CONFIDENCE:

        return (
            False,
            "The image could not be identified with sufficient confidence."
        )

    # --------------------------------------------------------
    # Very small difference between predictions
    # --------------------------------------------------------

    if margin < MIN_MARGIN:

        return (
            False,
            "The prediction is ambiguous. Please provide a clearer leaf image."
        )

    # --------------------------------------------------------
    # Valid prediction
    # --------------------------------------------------------

    return (
        True,
        "Prediction accepted."
    )