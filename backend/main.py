from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware

import tensorflow as tf
import numpy as np
from PIL import Image

import io
import os
import sys
import tempfile
import cv2


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
# FASTAPI
# ============================================================

app = FastAPI(
    title="PlantCare AI API",
    description=(
        "AI-powered plant disease detection, "
        "severity assessment and treatment recommendation."
    ),
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

# Configure production origins using:
#
# PLANTCARE_ALLOWED_ORIGINS
#
# Example:
#
# PLANTCARE_ALLOWED_ORIGINS=https://your-frontend.com
#
# Multiple origins can be separated by commas.
#
# Local development defaults are included so the existing
# local frontend/API workflow is not unnecessarily broken.

allowed_origins = os.getenv(
    "PLANTCARE_ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174,http://localhost:8501"
).split(",")

allowed_origins = [
    origin.strip()
    for origin in allowed_origins
    if origin.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST"
    ],
    allow_headers=[
        "Content-Type",
        "Authorization"
    ],
)


# ============================================================
# FILE SIZE LIMITS
# ============================================================

# Maximum image size:
# 10 MB

MAX_IMAGE_SIZE = 10 * 1024 * 1024


# Maximum video size:
# 50 MB

MAX_VIDEO_SIZE = 50 * 1024 * 1024


# ============================================================
# ALLOWED FILE TYPES
# ============================================================

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png"
}

ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png"
}


ALLOWED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".webm"
}


ALLOWED_VIDEO_CONTENT_TYPES = {
    "video/mp4",
    "video/x-msvideo",
    "video/quicktime",
    "video/x-matroska",
    "video/webm"
}


# ============================================================
# 15 SUPPORTED CLASSES
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
# TFLITE DISEASE MODEL
# ============================================================

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "plant_disease_model.tflite"
)

print(
    "Loading PlantCare AI disease model (TFLite)..."
)

disease_interpreter = tf.lite.Interpreter(
    model_path=MODEL_PATH,
    num_threads=1
)

disease_interpreter.allocate_tensors()

disease_input_details = (
    disease_interpreter.get_input_details()
)

disease_output_details = (
    disease_interpreter.get_output_details()
)

print(
    "PlantCare AI TFLite disease model loaded successfully."
)

print(
    "Disease model input:",
    disease_input_details[0]["shape"]
)

print(
    "Disease model output:",
    disease_output_details[0]["shape"]
)


# ============================================================
# CLASS NAME FORMATTER
# ============================================================

def format_class_name(class_name):

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
# TREATMENT FALLBACK
# ============================================================

def get_treatment(predicted_class):
    """
    Return treatment information for a prediction.

    If the treatment database does not contain an entry,
    return a consistent fallback instead of returning None.
    """

    treatment = TREATMENT_RECOMMENDATIONS.get(
        predicted_class
    )

    if treatment is not None:
        return treatment

    return {
        "plant": "Unknown",
        "condition": format_class_name(
            predicted_class
        ),
        "type": "Unknown",
        "pathogen": "Unknown",
        "target": "Unknown",
        "treatment_type": "General management",
        "active_ingredients": [],
        "chemical_guidance": (
            "No specific treatment recommendation "
            "is currently available for this prediction. "
            "Please consult a qualified agricultural "
            "professional before applying any treatment."
        ),
        "non_chemical": [
            "Monitor the plant closely.",
            "Remove severely affected plant material "
            "where appropriate.",
            "Maintain good plant hygiene and sanitation.",
            "Avoid unnecessary chemical application."
        ],
        "warning": (
            "No specific treatment database entry was "
            "found for this prediction. Do not apply "
            "chemicals without verifying the product label "
            "and crop-specific instructions."
        )
    }


# ============================================================
# VALIDATE PLANT / DISEASE COMPATIBILITY
# ============================================================

def validate_plant_prediction(
    validated_plant,
    predicted_class
):
    """
    Verify that the disease CNN prediction belongs
    to the plant identified by the plant validator.
    """

    allowed_classes = PLANT_CLASS_MAPPING.get(
        validated_plant,
        set()
    )

    return predicted_class in allowed_classes


# ============================================================
# FILE EXTENSION HELPER
# ============================================================

def get_file_extension(filename):
    """
    Safely obtain a lowercase file extension.
    """

    if not filename:
        return ""

    return os.path.splitext(
        filename
    )[1].lower()


# ============================================================
# IMAGE UPLOAD VALIDATION
# ============================================================

async def read_valid_image_upload(file):
    """
    Validate image extension, MIME type and file size,
    then decode the actual image contents.
    """

    extension = get_file_extension(
        file.filename
    )

    if extension not in ALLOWED_IMAGE_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported image format. "
                "Please upload JPG, JPEG or PNG."
            )
        )


    if (
        file.content_type
        and file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid image content type. "
                "Please upload a JPG, JPEG or PNG image."
            )
        )


    # Read at most MAX_IMAGE_SIZE + 1 bytes.
    # This prevents oversized files from being accepted.

    contents = await file.read(
        MAX_IMAGE_SIZE + 1
    )


    if len(contents) > MAX_IMAGE_SIZE:

        raise HTTPException(
            status_code=413,
            detail=(
                "Image file is too large. "
                "Maximum allowed size is 10 MB."
            )
        )


    try:

        image = Image.open(
            io.BytesIO(contents)
        )

        # Force Pillow to actually decode the image.
        image.verify()

        # Re-open after verify because verify() invalidates
        # the image object for normal processing.

        image = Image.open(
            io.BytesIO(contents)
        ).convert("RGB")

    except Exception:

        raise HTTPException(
            status_code=400,
            detail=(
                "Uploaded file is not a valid image."
            )
        )


    return image


# ============================================================
# VIDEO UPLOAD VALIDATION
# ============================================================

async def read_valid_video_upload(file):
    """
    Validate video extension, MIME type and file size.
    """

    extension = get_file_extension(
        file.filename
    )

    if extension not in ALLOWED_VIDEO_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported video format. "
                "Please upload MP4, AVI, MOV, MKV or WEBM."
            )
        )


    if (
        file.content_type
        and file.content_type not in ALLOWED_VIDEO_CONTENT_TYPES
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid video content type."
            )
        )


    # Read at most MAX_VIDEO_SIZE + 1 bytes.

    video_data = await file.read(
        MAX_VIDEO_SIZE + 1
    )


    if len(video_data) > MAX_VIDEO_SIZE:

        raise HTTPException(
            status_code=413,
            detail=(
                "Video file is too large. "
                "Maximum allowed size is 50 MB."
            )
        )


    if len(video_data) == 0:

        raise HTTPException(
            status_code=400,
            detail="Uploaded video file is empty."
        )


    return video_data


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "PlantCare AI API is running",
        "status": "online",
        "supported_classes": 15,
        "supported_plants": SUPPORTED_PLANTS,
        "plant_validator": "enabled"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model_loaded": True,
        "plant_validator_enabled": True,
        "supported_classes": 15,
        "supported_plants": SUPPORTED_PLANTS
    }


# ============================================================
# SUPPORTED CLASSES
# ============================================================

@app.get("/supported-classes")
def supported_classes():

    return {
        "total_classes": 15,

        "supported_plants":
            SUPPORTED_PLANTS,

        "classes": [
            format_class_name(name)
            for name in class_names
        ]
    }


# ============================================================
# CNN IMAGE PREDICTION
# ============================================================

def predict_image(image):

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

    # --------------------------------------------------------
    # TFLITE INPUT
    # --------------------------------------------------------

    input_index = (
        disease_input_details[0]["index"]
    )

    output_index = (
        disease_output_details[0]["index"]
    )

    disease_interpreter.set_tensor(
        input_index,
        image_array
    )

    disease_interpreter.invoke()

    prediction = (
        disease_interpreter.get_tensor(
            output_index
        )[0]
    )

    prediction = np.asarray(
        prediction,
        dtype=np.float32
    )

    # --------------------------------------------------------
    # PREDICTED CLASS
    # --------------------------------------------------------

    predicted_index = int(
        np.argmax(prediction)
    )

    predicted_class = class_names[
        predicted_index
    ]

    confidence = float(
        prediction[
            predicted_index
        ] * 100
    )

    return (
        predicted_class,
        confidence,
        prediction
    )


# ============================================================
# TOP 3 PREDICTIONS
# ============================================================

def get_top_predictions(prediction):

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
                "class":
                    format_class_name(
                        raw_class
                    ),

                "confidence":
                    round(
                        float(
                            prediction[index] * 100
                        ),
                        2
                    )
            }
        )

    return results


# ============================================================
# IMAGE PREDICTION ENDPOINT
# ============================================================

@app.post("/predict")
async def predict(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # ISSUE 10 — VALIDATE IMAGE UPLOAD
    # --------------------------------------------------------

    image = await read_valid_image_upload(
        file
    )


    # --------------------------------------------------------
    # STEP 1 — PLANT VALIDATOR
    # --------------------------------------------------------

    plant_validation = validate_plant_image(
        image
    )

    if not plant_validation["valid"]:

        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "prediction_status":
                    "Unsupported image",
                "message":
                    (
                        "This image does not contain "
                        "a supported plant."
                    ),
                "reason":
                    plant_validation.get(
                        "reason",
                        "Unsupported plant or no-plant image detected."
                    ),
                "visual_score":
                    plant_validation.get(
                        "visual_score",
                        None
                    ),
                "supported_plants":
                    SUPPORTED_PLANTS,
                "supported_classes":
                    15,
                "note":
                    (
                        "PlantCare AI currently supports "
                        "Tomato, Potato and Bell Pepper."
                    )
            }
        )


    # --------------------------------------------------------
    # STEP 2 — CNN DISEASE PREDICTION
    # --------------------------------------------------------

    (
        predicted_class,
        confidence,
        prediction
    ) = predict_image(
        image
    )


    # --------------------------------------------------------
    # STEP 2.5 — PLANT / DISEASE COMPATIBILITY CHECK
    # --------------------------------------------------------

    validated_plant = plant_validation.get(
        "plant"
    )

    plant_prediction_valid = (
        validate_plant_prediction(
            validated_plant,
            predicted_class
        )
    )

    if not plant_prediction_valid:

        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "prediction_status":
                    "Plant prediction mismatch",
                "message":
                    (
                        "The plant validator and disease "
                        "classifier produced inconsistent "
                        "results. Please provide a clearer "
                        "leaf image."
                    ),
                "validated_plant":
                    validated_plant,
                "predicted_class":
                    format_class_name(
                        predicted_class
                    ),
                "confidence":
                    round(
                        confidence,
                        2
                    ),
                "supported_plants":
                    SUPPORTED_PLANTS,
                "supported_classes":
                    15
            }
        )


    # --------------------------------------------------------
    # STEP 3 — CONFIDENCE VALIDATION
    # --------------------------------------------------------

    is_valid, validation_message = (
        validate_prediction(
            prediction
        )
    )

    if not is_valid:

        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "prediction_status":
                    "Uncertain",
                "message":
                    validation_message,
                "confidence":
                    round(
                        confidence,
                        2
                    ),
                "supported_plants":
                    SUPPORTED_PLANTS,
                "supported_classes":
                    15
            }
        )


    # --------------------------------------------------------
    # STEP 4 — TOP 3
    # --------------------------------------------------------

    top_predictions = get_top_predictions(
        prediction
    )


    # --------------------------------------------------------
    # STEP 5 — HEALTHY PLANT
    # --------------------------------------------------------

    if predicted_class in HEALTHY_CLASSES:

        treatment = get_treatment(
            predicted_class
        )

        return {

            "success": True,

            "prediction": {

                "class":
                    format_class_name(
                        predicted_class
                    ),

                "confidence":
                    round(
                        confidence,
                        2
                    ),

                "plant_status":
                    "Healthy",

                "disease_detected":
                    False
            },

            "top_3_predictions":
                top_predictions,

            "severity": {

                "affected_area_percentage":
                    0,

                "level":
                    "No disease"
            },

            "treatment":
                treatment
        }


    # --------------------------------------------------------
    # STEP 6 — DISEASE SEVERITY
    # --------------------------------------------------------

    try:

        (
            affected_percentage,
            severity_level,
            _
        ) = analyze_severity(
            image
        )

    except Exception as error:

        print(
            f"Severity analysis error: {error}"
        )

        affected_percentage = 0
        severity_level = "Unknown"


    # --------------------------------------------------------
    # STEP 7 — TREATMENT
    # --------------------------------------------------------

    treatment = get_treatment(
        predicted_class
    )


    # --------------------------------------------------------
    # STEP 8 — FINAL IMAGE RESPONSE
    # --------------------------------------------------------

    return {

        "success": True,

        "prediction": {

            "class":
                format_class_name(
                    predicted_class
                ),

            "confidence":
                round(
                    confidence,
                    2
                ),

            "plant_status":
                "Disease detected",

            "disease_detected":
                True
        },

        "top_3_predictions":
            top_predictions,

        "severity": {

            "affected_area_percentage":
                round(
                    float(
                        affected_percentage
                    ),
                    2
                ),

            "level":
                severity_level
        },

        "treatment":
            treatment
    }


# ============================================================
# VIDEO ANALYSIS
# ============================================================

@app.post("/analyze-video")
async def analyze_video(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # ISSUE 10 — VALIDATE VIDEO UPLOAD
    # --------------------------------------------------------

    video_data = await read_valid_video_upload(
        file
    )


    # --------------------------------------------------------
    # SAVE TEMPORARY VIDEO
    # --------------------------------------------------------

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=get_file_extension(
            file.filename
        ) or ".mp4"
    )

    temp_file.write(
        video_data
    )

    temp_file.close()

    video_path = temp_file.name


    capture = None


    try:

        # ----------------------------------------------------
        # OPEN VIDEO
        # ----------------------------------------------------

        capture = cv2.VideoCapture(
            video_path
        )

        if not capture.isOpened():

            raise HTTPException(
                status_code=400,
                detail=(
                    "Unable to open the uploaded video. "
                    "Please provide a valid video file."
                )
            )


        total_frames = int(
            capture.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )

        fps = capture.get(
            cv2.CAP_PROP_FPS
        )

        if fps <= 0:

            fps = 30


        duration = (
            total_frames / fps
        )


        # ----------------------------------------------------
        # SELECT FRAMES
        # ----------------------------------------------------

        max_samples = 20

        if total_frames <= max_samples:

            frame_indices = list(
                range(total_frames)
            )

        else:

            frame_indices = np.linspace(
                0,
                total_frames - 1,
                max_samples,
                dtype=int
            )


        # ----------------------------------------------------
        # STORAGE
        # ----------------------------------------------------

        frame_results = []

        prediction_counts = {}

        severity_values = []

        affected_percentages = []


        # ----------------------------------------------------
        # FRAME COUNTERS
        # ----------------------------------------------------

        supported_frame_count = 0

        unsupported_frame_count = 0

        uncertain_frame_count = 0

        usable_frame_count = 0

        successfully_read_frames = 0

        plant_counts = {}


        # ----------------------------------------------------
        # ANALYZE VIDEO FRAMES
        # ----------------------------------------------------

        for frame_number in frame_indices:

            # ------------------------------------------------
            # READ FRAME
            # ------------------------------------------------

            capture.set(
                cv2.CAP_PROP_POS_FRAMES,
                int(frame_number)
            )

            success, frame = capture.read()

            if not success:

                continue


            successfully_read_frames += 1


            # ------------------------------------------------
            # CONVERT FRAME
            # ------------------------------------------------

            frame_rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            image = Image.fromarray(
                frame_rgb
            ).convert("RGB")


            # ------------------------------------------------
            # STEP 1 — PLANT VALIDATOR
            # ------------------------------------------------

            plant_validation = (
                validate_plant_image(
                    image
                )
            )


            if not plant_validation["valid"]:

                unsupported_frame_count += 1

                validated_plant = (
                    plant_validation.get(
                        "plant"
                    )
                )

                continue


            # ------------------------------------------------
            # FRAME PASSED PLANT VALIDATOR
            # ------------------------------------------------

            supported_frame_count += 1


            # ------------------------------------------------
            # STEP 2 — CNN PREDICTION
            # ------------------------------------------------

            (
                predicted_class,
                confidence,
                prediction
            ) = predict_image(
                image
            )


            # ------------------------------------------------
            # STEP 2.5 — PLANT / DISEASE COMPATIBILITY
            # ------------------------------------------------

            validated_plant = (
                plant_validation.get(
                    "plant"
                )
            )

            plant_prediction_valid = (
                validate_plant_prediction(
                    validated_plant,
                    predicted_class
                )
            )

            if not plant_prediction_valid:

                uncertain_frame_count += 1

                continue


            # ------------------------------------------------
            # TRACK VALIDATED PLANT
            # ------------------------------------------------

            plant_counts[
                validated_plant
            ] = plant_counts.get(
                validated_plant,
                0
            ) + 1


            # ------------------------------------------------
            # STEP 3 — CONFIDENCE VALIDATION
            # ------------------------------------------------

            is_valid, validation_message = (
                validate_prediction(
                    prediction
                )
            )

            if not is_valid:

                uncertain_frame_count += 1

                continue


            # ------------------------------------------------
            # FRAME IS USABLE
            # ------------------------------------------------

            usable_frame_count += 1


            # ------------------------------------------------
            # COUNT PREDICTION
            # ------------------------------------------------

            prediction_counts[
                predicted_class
            ] = prediction_counts.get(
                predicted_class,
                0
            ) + 1


            # ------------------------------------------------
            # HEALTHY FRAME
            # ------------------------------------------------

            if predicted_class in HEALTHY_CLASSES:

                frame_results.append(
                    {

                        "frame":
                            int(frame_number),

                        "prediction":
                            format_class_name(
                                predicted_class
                            ),

                        "confidence":
                            round(
                                confidence,
                                2
                            ),

                        "affected_area_percentage":
                            0.0,

                        "severity":
                            "No disease"
                    }
                )

                continue


            # ------------------------------------------------
            # DISEASE SEVERITY
            # ------------------------------------------------

            try:

                (
                    affected_percentage,
                    severity_level,
                    _
                ) = analyze_severity(
                    image
                )

            except Exception as error:

                print(
                    f"Video severity error: {error}"
                )

                affected_percentage = 0.0

                severity_level = "Unknown"


            affected_percentages.append(
                float(
                    affected_percentage
                )
            )


            # ------------------------------------------------
            # SEVERITY SCORE
            # ------------------------------------------------

            severity_score = {

                "Mild": 1,

                "Moderate": 2,

                "Severe": 3

            }.get(
                severity_level,
                0
            )


            if severity_score > 0:

                severity_values.append(
                    severity_score
                )


            # ------------------------------------------------
            # STORE FRAME RESULT
            # ------------------------------------------------

            frame_results.append(
                {

                    "frame":
                        int(frame_number),

                    "prediction":
                        format_class_name(
                            predicted_class
                        ),

                    "confidence":
                        round(
                            confidence,
                            2
                        ),

                    "affected_area_percentage":
                        round(
                            float(
                                affected_percentage
                            ),
                            2
                        ),

                    "severity":
                        severity_level
                }
            )


        # ----------------------------------------------------
        # CLOSE VIDEO
        # ----------------------------------------------------

        capture.release()
        capture = None


        # ----------------------------------------------------
        # VIDEO COUNTER SUMMARY
        # ----------------------------------------------------

        print()
        print("=" * 60)
        print("VIDEO ANALYSIS SUMMARY")
        print("=" * 60)

        print(
            f"Requested sampled frames: "
            f"{len(frame_indices)}"
        )

        print(
            f"Successfully read frames: "
            f"{successfully_read_frames}"
        )

        print(
            f"Supported frames: "
            f"{supported_frame_count}"
        )

        print(
            f"Unsupported frames: "
            f"{unsupported_frame_count}"
        )

        print(
            f"Uncertain frames: "
            f"{uncertain_frame_count}"
        )

        print(
            f"Usable frames: "
            f"{usable_frame_count}"
        )

        print("=" * 60)


        # ----------------------------------------------------
        # NO USABLE FRAMES
        # ----------------------------------------------------

        if not frame_results:

            raise HTTPException(
                status_code=422,
                detail={
                    "success": False,

                    "prediction_status":
                        "Unsupported or uncertain video",

                    "error":
                        (
                            "No suitable supported-plant "
                            "frames were detected."
                        ),

                    "frames_analyzed":
                        successfully_read_frames,

                    "usable_frames":
                        0,

                    "supported_frames":
                        supported_frame_count,

                    "unsupported_frames":
                        unsupported_frame_count,

                    "uncertain_frames":
                        uncertain_frame_count,

                    "supported_plants":
                        SUPPORTED_PLANTS
                }
            )


        # ----------------------------------------------------
        # DOMINANT CLASS
        # ----------------------------------------------------

        class_confidences = {}

        for item in frame_results:

            prediction_name = item[
                "prediction"
            ]

            raw_class = None

            for class_name in class_names:

                if (
                    format_class_name(
                        class_name
                    )
                    == prediction_name
                ):

                    raw_class = class_name

                    break


            if raw_class is None:

                continue


            if raw_class not in class_confidences:

                class_confidences[
                    raw_class
                ] = []


            class_confidences[
                raw_class
            ].append(
                item["confidence"]
            )


        dominant_class = max(
            prediction_counts,
            key=lambda class_name: (
                prediction_counts[
                    class_name
                ],
                np.mean(
                    class_confidences.get(
                        class_name,
                        [0.0]
                    )
                )
            )
        )


        # ----------------------------------------------------
        # DOMINANT PLANT
        # ----------------------------------------------------

        dominant_plant = max(
            plant_counts,
            key=plant_counts.get
        )


        # ----------------------------------------------------
        # AVERAGE CONFIDENCE
        # ----------------------------------------------------

        average_confidence = np.mean(
            [
                item["confidence"]
                for item in frame_results
            ]
        )


        # ----------------------------------------------------
        # HEALTHY VIDEO
        # ----------------------------------------------------

        if dominant_class in HEALTHY_CLASSES:

            treatment = get_treatment(
                dominant_class
            )


            return {

                "success": True,

                "video": {

                    "duration_seconds":
                        round(
                            duration,
                            2
                        ),

                    "total_frames":
                        total_frames,

                    "frames_analyzed":
                        successfully_read_frames,

                    "usable_frames":
                        usable_frame_count,

                    "supported_frames":
                        supported_frame_count,

                    "unsupported_frames":
                        unsupported_frame_count,

                    "uncertain_frames":
                        uncertain_frame_count
                },

                "overall_result": {

                    "plant":
                        dominant_plant,

                    "dominant_disease":
                        format_class_name(
                            dominant_class
                        ),

                    "average_confidence":
                        round(
                            float(
                                average_confidence
                            ),
                            2
                        ),

                    "average_affected_area_percentage":
                        0.0,

                    "overall_severity":
                        "No disease",

                    "plant_status":
                        "Healthy",

                    "disease_detected":
                        False
                },

                "disease_distribution": {

                    format_class_name(
                        name
                    ): count

                    for (
                        name,
                        count
                    ) in prediction_counts.items()
                },

                "frame_results":
                    frame_results,

                "treatment":
                    treatment
            }


        # ----------------------------------------------------
        # DISEASE VIDEO
        # ----------------------------------------------------

        if affected_percentages:

            average_affected_area = np.mean(
                affected_percentages
            )

        else:

            average_affected_area = 0.0


        # ----------------------------------------------------
        # OVERALL SEVERITY
        # ----------------------------------------------------

        if severity_values:

            average_severity_score = np.mean(
                severity_values
            )

            if average_severity_score < 1.5:

                overall_severity = "Mild"

            elif average_severity_score < 2.5:

                overall_severity = "Moderate"

            else:

                overall_severity = "Severe"

        else:

            overall_severity = "Unknown"


        # ----------------------------------------------------
        # TREATMENT
        # ----------------------------------------------------

        treatment = get_treatment(
            dominant_class
        )


        # ----------------------------------------------------
        # FINAL VIDEO RESPONSE
        # ----------------------------------------------------

        return {

            "success": True,

            "video": {

                "duration_seconds":
                    round(
                        duration,
                        2
                    ),

                "total_frames":
                    total_frames,

                "frames_analyzed":
                    successfully_read_frames,

                "usable_frames":
                    usable_frame_count,

                "supported_frames":
                    supported_frame_count,

                "unsupported_frames":
                    unsupported_frame_count,

                "uncertain_frames":
                    uncertain_frame_count
            },

            "overall_result": {

                "plant":
                    dominant_plant,

                "dominant_disease":
                    format_class_name(
                        dominant_class
                    ),

                "average_confidence":
                    round(
                        float(
                            average_confidence
                        ),
                        2
                    ),

                "average_affected_area_percentage":
                    round(
                        float(
                            average_affected_area
                        ),
                        2
                    ),

                "overall_severity":
                    overall_severity,

                "plant_status":
                    "Disease detected",

                "disease_detected":
                    True
            },

            "disease_distribution": {

                format_class_name(
                    name
                ): count

                for (
                    name,
                    count
                ) in prediction_counts.items()
            },

            "frame_results":
                frame_results,

            "treatment":
                treatment
        }


    finally:

        # ----------------------------------------------------
        # RELEASE VIDEO CAPTURE
        # ----------------------------------------------------

        if capture is not None:

            try:

                capture.release()

            except Exception as error:

                print(
                    f"Video capture cleanup error: {error}"
                )


        # ----------------------------------------------------
        # GUARANTEED TEMP FILE CLEANUP
        # ----------------------------------------------------

        try:

            if os.path.exists(
                video_path
            ):

                os.remove(
                    video_path
                )

        except Exception as error:

            print(
                f"Temporary file cleanup error: {error}"
            )