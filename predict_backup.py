import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image

# -----------------------------------
# Page Configuration
# -----------------------------------
st.set_page_config(
    page_title="Plant Disease Detection",
    page_icon="🌿",
    layout="centered"
)

# -----------------------------------
# Title
# -----------------------------------
st.title("🌿 Plant Disease Detection")
st.write("Upload a plant leaf image to detect its disease.")

# -----------------------------------
# Load Trained Model
# -----------------------------------
@st.cache_resource
def load_model():
    return tf.keras.models.load_model(
        "models/plant_disease_model.keras"
    )

model = load_model()

# -----------------------------------
# Disease Classes
# -----------------------------------
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

# -----------------------------------
# Upload Image
# -----------------------------------
uploaded_file = st.file_uploader(
    "Upload a plant leaf image",
    type=["jpg", "jpeg", "png"]
)

# -----------------------------------
# Prediction
# -----------------------------------
if uploaded_file is not None:

    image = Image.open(uploaded_file).convert("RGB")

    st.image(
        image,
        caption="Uploaded Leaf Image",
        use_container_width=True
    )

    if st.button("🔍 Predict Disease"):

        # Resize image
        image = image.resize((224, 224))

        # Convert image to array
        image_array = np.array(image)

        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)

        # Make prediction
        prediction = model.predict(image_array, verbose=0)

        # Get predicted class
        predicted_index = np.argmax(prediction[0])

        predicted_class = class_names[predicted_index]

        # Get confidence
        confidence = prediction[0][predicted_index] * 100

        # -----------------------------------
        # Display Result
        # -----------------------------------
        st.success("Prediction Completed!")

        st.subheader("🌱 Prediction Result")

        st.write(
            f"**Disease:** {predicted_class}"
        )

        st.write(
            f"**Confidence:** {confidence:.2f}%"
        )