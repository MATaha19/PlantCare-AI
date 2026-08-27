import os
import sys

import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# ============================================================
# BACKEND MODULES
# ============================================================

from backend.severity import analyze_severity
from backend.validation import validate_prediction
from backend.plant_validator import validate_plant_image

from data.treatment_recommendations import (
    TREATMENT_RECOMMENDATIONS
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PlantCare AI",
    page_icon="🌿",
    layout="wide"
)


# ============================================================
# SUPPORTED DISEASE CLASSES
# ============================================================

class_names = [
    "Pepper__bell___Bacterial_spot",
    "Pepper__bell___healthy",

    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",

    "Tomato_Bacterial_spot",
    "Tomato_Early_blight",
    "Tomato_Late_blight",
    "Tomato_Leaf_Mold",
    "Tomato_Septoria_leaf_spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite",
    "Tomato__Target_Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus",
    "Tomato__Tomato_mosaic_virus",
    "Tomato_healthy"
]


# ============================================================
# HEALTHY CLASSES
# ============================================================

HEALTHY_CLASSES = {
    "Pepper__bell___healthy",
    "Potato___healthy",
    "Tomato_healthy"
}


# ============================================================
# SUPPORTED PLANTS
# ============================================================

SUPPORTED_PLANTS = [
    "Tomato",
    "Potato",
    "Bell Pepper"
]


# ============================================================
# PLANT → DISEASE CLASS MAPPING
# ============================================================

PLANT_CLASS_MAPPING = {

    "Tomato": {
        "Tomato_Bacterial_spot",
        "Tomato_Early_blight",
        "Tomato_Late_blight",
        "Tomato_Leaf_Mold",
        "Tomato_Septoria_leaf_spot",
        "Tomato_Spider_mites_Two_spotted_spider_mite",
        "Tomato__Target_Spot",
        "Tomato__Tomato_YellowLeaf__Curl_Virus",
        "Tomato__Tomato_mosaic_virus",
        "Tomato_healthy"
    },

    "Potato": {
        "Potato___Early_blight",
        "Potato___Late_blight",
        "Potato___healthy"
    },

    "Bell Pepper": {
        "Pepper__bell___Bacterial_spot",
        "Pepper__bell___healthy"
    }
}


# ============================================================
# MODEL PATH
# ============================================================

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "plant_disease_model.keras"
)


# ============================================================
# LOAD TRAINED CNN MODEL
# ============================================================

@st.cache_resource
def load_model():

    if not os.path.exists(MODEL_PATH):

        raise FileNotFoundError(
            "Disease model not found: "
            f"{MODEL_PATH}"
        )

    return tf.keras.models.load_model(
        MODEL_PATH
    )


model = load_model()


# ============================================================
# CLASS NAME FORMATTER
# ============================================================

def format_class_name(
    class_name
):

    names = {

        "Pepper__bell___Bacterial_spot":
            "Bell Pepper — Bacterial Spot",

        "Pepper__bell___healthy":
            "Bell Pepper — Healthy",

        "Potato___Early_blight":
            "Potato — Early Blight",

        "Potato___Late_blight":
            "Potato — Late Blight",

        "Potato___healthy":
            "Potato — Healthy",

        "Tomato_Bacterial_spot":
            "Tomato — Bacterial Spot",

        "Tomato_Early_blight":
            "Tomato — Early Blight",

        "Tomato_Late_blight":
            "Tomato — Late Blight",

        "Tomato_Leaf_Mold":
            "Tomato — Leaf Mold",

        "Tomato_Septoria_leaf_spot":
            "Tomato — Septoria Leaf Spot",

        "Tomato_Spider_mites_Two_spotted_spider_mite":
            "Tomato — Spider Mites",

        "Tomato__Target_Spot":
            "Tomato — Target Spot",

        "Tomato__Tomato_YellowLeaf__Curl_Virus":
            "Tomato — Yellow Leaf Curl Virus",

        "Tomato__Tomato_mosaic_virus":
            "Tomato — Mosaic Virus",

        "Tomato_healthy":
            "Tomato — Healthy"
    }

    return names.get(
        class_name,
        class_name
    )


# ============================================================
# PLANT / DISEASE COMPATIBILITY
# ============================================================

def validate_plant_prediction(
    validated_plant,
    predicted_class
):

    allowed_classes = PLANT_CLASS_MAPPING.get(
        validated_plant,
        set()
    )

    return predicted_class in allowed_classes


# ============================================================
# IMAGE PREDICTION
# ============================================================

def predict_image(
    image
):
    """
    Run the disease CNN.

    IMPORTANT:
    Do NOT divide the image by 255 here.

    The trained disease model expects the same raw
    0-255 preprocessing used by the working API.
    """

    processed_image = image.resize(
        (224, 224)
    )

    image_array = np.array(
        processed_image,
        dtype=np.float32
    )

    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    prediction = model.predict(
        image_array,
        verbose=0
    )[0]

    prediction = np.asarray(
        prediction,
        dtype=np.float32
    ).flatten()

    if len(prediction) != len(
        class_names
    ):

        raise ValueError(
            "Disease model output count does not match "
            "the configured class_names list. "
            f"Model output: {len(prediction)}, "
            f"Class names: {len(class_names)}."
        )

    predicted_index = int(
        np.argmax(
            prediction
        )
    )

    predicted_class = class_names[
        predicted_index
    ]

    confidence = float(
        prediction[
            predicted_index
        ] * 100.0
    )

    return (
        predicted_class,
        confidence,
        prediction
    )


# ============================================================
# TOP 3 PREDICTIONS
# ============================================================

def get_top_predictions(
    prediction
):

    top_indices = np.argsort(
        prediction
    )[::-1][:3]

    results = []

    for index in top_indices:

        raw_class = class_names[
            int(index)
        ]

        results.append(
            {
                "class": format_class_name(
                    raw_class
                ),
                "confidence": round(
                    float(
                        prediction[
                            index
                        ] * 100.0
                    ),
                    2
                )
            }
        )

    return results


# ============================================================
# HEADER
# ============================================================

st.title(
    "🌿 Plant Disease AI"
)

st.subheader(
    "AI-powered plant disease detection, severity "
    "estimation and treatment recommendation"
)

st.write(
    "Upload a plant leaf image to identify the most "
    "likely disease, estimate visible affected area "
    "and receive general treatment and prevention "
    "guidance."
)

st.divider()


# ============================================================
# IMAGE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "📤 Upload a plant leaf image",
    type=[
        "jpg",
        "jpeg",
        "png"
    ]
)


# ============================================================
# MAIN PROCESSING
# ============================================================

if uploaded_file is not None:

    # --------------------------------------------------------
    # READ IMAGE
    # --------------------------------------------------------

    try:

        original_image = Image.open(
            uploaded_file
        ).convert("RGB")

    except Exception as error:

        st.error(
            "❌ Unable to read the uploaded image."
        )

        st.write(
            f"Error: {error}"
        )

        st.stop()


    # --------------------------------------------------------
    # DISPLAY IMAGE
    # --------------------------------------------------------

    st.subheader(
        "🖼️ Uploaded Plant Image"
    )

    st.image(
        original_image,
        caption="Original Leaf Image",
        use_container_width=True
    )

    st.divider()


    # --------------------------------------------------------
    # PREDICTION BUTTON
    # --------------------------------------------------------

    if st.button(
        "🔍 Detect Disease & Analyze Severity",
        use_container_width=True
    ):

        with st.spinner(
            "Analyzing the plant leaf..."
        ):

            # =================================================
            # STEP 1 — PLANT VALIDATION
            # =================================================

            plant_validation = validate_plant_image(
                original_image
            )


            if not plant_validation.get(
                "valid",
                False
            ):

                st.error(
                    "❌ Unsupported image"
                )

                rejection_message = (
                    plant_validation.get(
                        "message",
                        "The uploaded image does not "
                        "contain a supported plant."
                    )
                )

                rejection_reason = (
                    plant_validation.get(
                        "reason",
                        "Unknown"
                    )
                )

                rejection_visual_score = (
                    plant_validation.get(
                        "visual_score",
                        "N/A"
                    )
                )

                st.warning(
                    rejection_message
                )

                st.write(
                    f"**Reason:** {rejection_reason}"
                )

                st.write(
                    f"**Visual Score:** "
                    f"{rejection_visual_score}"
                )

                st.info(
                    "PlantCare AI currently supports: "
                    + ", ".join(
                        SUPPORTED_PLANTS
                    )
                )

                st.stop()


            # =================================================
            # VALIDATED PLANT
            # =================================================

            validated_plant = (
                plant_validation.get(
                    "plant",
                    "Unknown"
                )
            )

            validator_confidence = (
                plant_validation.get(
                    "confidence",
                    None
                )
            )

            visual_score = (
                plant_validation.get(
                    "visual_score",
                    0.0
                )
            )


            # =================================================
            # STEP 2 — DISEASE CNN
            # =================================================

            try:

                (
                    predicted_class,
                    confidence,
                    prediction
                ) = predict_image(
                    original_image
                )

            except Exception as error:

                st.error(
                    "❌ Disease classification failed."
                )

                st.write(
                    f"Error: {error}"
                )

                st.stop()


            # =================================================
            # STEP 2.5 — PLANT / DISEASE COMPATIBILITY
            # =================================================

            plant_prediction_valid = (
                validate_plant_prediction(
                    validated_plant,
                    predicted_class
                )
            )


            if not plant_prediction_valid:

                st.error(
                    "❌ Plant and disease prediction mismatch"
                )

                formatted_prediction = (
                    format_class_name(
                        predicted_class
                    )
                )

                st.warning(
                    "The plant validator detected "
                    f"{validated_plant}, but the disease "
                    "classifier predicted "
                    f"{formatted_prediction}."
                )

                st.info(
                    "The result has been rejected to prevent "
                    "an incorrect disease recommendation."
                )

                st.write(
                    f"**Validated Plant:** "
                    f"{validated_plant}"
                )

                st.write(
                    f"**CNN Prediction:** "
                    f"{formatted_prediction}"
                )

                st.write(
                    f"**CNN Confidence:** "
                    f"{confidence:.2f}%"
                )

                st.stop()


            # =================================================
            # STEP 3 — CONFIDENCE VALIDATION
            # =================================================

            (
                is_valid,
                validation_message
            ) = validate_prediction(
                prediction
            )


            if not is_valid:

                st.warning(
                    "⚠️ Prediction Uncertain"
                )

                st.write(
                    validation_message
                )

                st.metric(
                    "CNN Confidence",
                    f"{confidence:.2f}%"
                )

                st.info(
                    "Please upload a clearer image of "
                    "the plant leaf."
                )

                st.stop()


            # =================================================
            # STEP 4 — TOP 3
            # =================================================

            top_predictions = get_top_predictions(
                prediction
            )


            # =================================================
            # STEP 5 — SEVERITY
            # =================================================

            if predicted_class in HEALTHY_CLASSES:

                affected_percentage = 0.0

                severity_level = (
                    "No disease"
                )

                highlighted_image = None

            else:

                try:

                    (
                        affected_percentage,
                        severity_level,
                        highlighted_image
                    ) = analyze_severity(
                        original_image
                    )

                except Exception as error:

                    print(
                        f"Severity analysis error: {error}"
                    )

                    affected_percentage = 0.0

                    severity_level = (
                        "Unknown"
                    )

                    highlighted_image = None


            # =================================================
            # STEP 6 — TREATMENT
            # =================================================

            info = (
                TREATMENT_RECOMMENDATIONS.get(
                    predicted_class
                )
            )


        # =====================================================
        # ANALYSIS COMPLETED
        # =====================================================

        st.success(
            "✅ Analysis Completed"
        )

        st.divider()


        # =====================================================
        # RESULT SUMMARY
        # =====================================================

        st.subheader(
            "🌱 Detection Result"
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )


        with col1:

            st.metric(
                "Plant",
                validated_plant
            )


        with col2:

            condition = (
                info["condition"]
                if info
                else format_class_name(
                    predicted_class
                )
            )

            st.metric(
                "Condition",
                condition
            )


        with col3:

            st.metric(
                "Confidence",
                f"{confidence:.2f}%"
            )


        with col4:

            st.metric(
                "Affected Area",
                f"{affected_percentage:.2f}%"
            )


        # =====================================================
        # VALIDATOR INFORMATION
        # =====================================================

        with st.expander(
            "🌿 Plant Validation Details"
        ):

            st.write(
                f"**Detected Plant:** "
                f"{validated_plant}"
            )

            if validator_confidence is not None:

                st.write(
                    f"**Plant Validator Confidence:** "
                    f"{float(validator_confidence):.2f}%"
                )

            st.write(
                f"**Visual Score:** "
                f"{visual_score}"
            )

            validation_reason = (
                plant_validation.get(
                    "reason",
                    "N/A"
                )
            )

            st.write(
                f"**Validation Reason:** "
                f"{validation_reason}"
            )

            st.write(
                "**Plant Validation:** Passed"
            )


        # =====================================================
        # SEVERITY
        # =====================================================

        st.subheader(
            "📊 Severity Assessment"
        )


        if severity_level == "No disease":

            st.success(
                "🟢 No disease detected"
            )

        elif severity_level == "Mild":

            st.success(
                f"🟢 Mild — "
                f"{affected_percentage:.2f}% "
                f"estimated affected area"
            )

        elif severity_level == "Moderate":

            st.warning(
                f"🟡 Moderate — "
                f"{affected_percentage:.2f}% "
                f"estimated affected area"
            )

        elif severity_level == "Severe":

            st.error(
                f"🔴 Severe — "
                f"{affected_percentage:.2f}% "
                f"estimated affected area"
            )

        else:

            st.warning(
                "⚠️ Severity could not be reliably determined."
            )


        st.caption(
            "The affected-area percentage is an "
            "image-processing estimate and should be "
            "treated as a screening indicator, not a "
            "laboratory measurement."
        )


        # =====================================================
        # IMAGE COMPARISON
        # =====================================================

        if highlighted_image is not None:

            st.divider()

            st.subheader(
                "🖼️ Visual Analysis"
            )

            image_col1, image_col2 = (
                st.columns(2)
            )


            with image_col1:

                st.markdown(
                    "### Original Image"
                )

                st.image(
                    original_image,
                    use_container_width=True
                )


            with image_col2:

                st.markdown(
                    "### Severity Visualization"
                )

                st.image(
                    highlighted_image,
                    use_container_width=True
                )


        # =====================================================
        # TOP 3 PREDICTIONS
        # =====================================================

        st.divider()

        st.subheader(
            "🏆 Top 3 CNN Predictions"
        )


        for position, item in enumerate(
            top_predictions,
            start=1
        ):

            st.write(
                f"**{position}. "
                f"{item['class']}** — "
                f"{item['confidence']:.2f}%"
            )


        # =====================================================
        # DISEASE INFORMATION
        # =====================================================

        st.divider()

        st.subheader(
            "📋 Disease Information"
        )


        if info:

            info_col1, info_col2 = (
                st.columns(2)
            )


            with info_col1:

                st.write(
                    f"**Plant:** "
                    f"{info['plant']}"
                )

                st.write(
                    f"**Condition:** "
                    f"{info['condition']}"
                )

                st.write(
                    f"**Disease/Pest Type:** "
                    f"{info['type']}"
                )


            with info_col2:

                st.write(
                    f"**Pathogen/Pest:** "
                    f"{info['pathogen']}"
                )

                st.write(
                    f"**Target:** "
                    f"{info['target']}"
                )

        else:

            st.warning(
                "No treatment database entry was found "
                "for this prediction."
            )


        # =====================================================
        # CHEMICAL TREATMENT
        # =====================================================

        st.divider()

        st.subheader(
            "🧪 Recommended Chemical Treatment"
        )


        if info:

            st.info(
                f"**Treatment Type:** "
                f"{info['treatment_type']}"
            )


            if info["active_ingredients"]:

                st.markdown(
                    "#### Active Ingredient(s)"
                )


                for ingredient in info[
                    "active_ingredients"
                ]:

                    st.write(
                        f"• **{ingredient}**"
                    )

            else:

                st.write(
                    "No direct chemical treatment "
                    "is recommended."
                )


            st.markdown(
                "#### 🎯 Treatment Guidance"
            )

            st.write(
                info["chemical_guidance"]
            )


        # =====================================================
        # NON-CHEMICAL MANAGEMENT
        # =====================================================

        if info:

            st.subheader(
                "🌿 Non-Chemical Management"
            )


            for action in info[
                "non_chemical"
            ]:

                st.write(
                    f"• {action}"
                )


        # =====================================================
        # SAFETY WARNING
        # =====================================================

        if info:

            st.subheader(
                "⚠️ Important Safety Information"
            )

            st.warning(
                info["warning"]
            )


        st.caption(
            "Chemical recommendations are general "
            "active-ingredient guidance. Always verify "
            "that the specific commercial product is "
            "registered/labeled for the crop and condition "
            "in your region. Follow the product label for "
            "application rate, PPE, re-entry interval and "
            "pre-harvest interval."
        )


        # =====================================================
        # TECHNICAL DETAILS
        # =====================================================

        with st.expander(
            "🔬 View Technical Details"
        ):

            st.write(
                f"**Validated Plant:** "
                f"{validated_plant}"
            )

            st.write(
                f"**Predicted Class:** "
                f"{predicted_class}"
            )

            formatted_prediction = (
                format_class_name(
                    predicted_class
                )
            )

            st.write(
                f"**Formatted Prediction:** "
                f"{formatted_prediction}"
            )

            class_index = class_names.index(
                predicted_class
            )

            st.write(
                f"**Class Index:** "
                f"{class_index}"
            )

            st.write(
                f"**CNN Confidence:** "
                f"{confidence:.2f}%"
            )

            if validator_confidence is not None:

                st.write(
                    f"**Plant Validator Confidence:** "
                    f"{float(validator_confidence):.2f}%"
                )

            st.write(
                f"**Plant Visual Score:** "
                f"{visual_score}"
            )

            st.write(
                f"**Estimated Affected Area:** "
                f"{affected_percentage:.2f}%"
            )

            st.write(
                f"**Severity:** "
                f"{severity_level}"
            )

            st.write(
                "**Input Size:** 224 × 224 pixels"
            )