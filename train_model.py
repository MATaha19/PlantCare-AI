import tensorflow as tf
from tensorflow.keras import layers, models
import os

# -----------------------------
# Dataset Path
# -----------------------------
dataset_path = "PlantVillage"

# -----------------------------
# Load Training Dataset
# -----------------------------
train_dataset = tf.keras.preprocessing.image_dataset_from_directory(
    dataset_path,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=(224, 224),
    batch_size=32
)

# -----------------------------
# Load Validation Dataset
# -----------------------------
val_dataset = tf.keras.preprocessing.image_dataset_from_directory(
    dataset_path,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=(224, 224),
    batch_size=32
)

# -----------------------------
# Save Class Names
# -----------------------------
class_names = train_dataset.class_names

print("\nPlant Disease Classes:")
print(class_names)
print(f"\nTotal Classes: {len(class_names)}")

# -----------------------------
# Optimize Performance
# -----------------------------
AUTOTUNE = tf.data.AUTOTUNE

train_dataset = train_dataset.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_dataset = val_dataset.cache().prefetch(buffer_size=AUTOTUNE)

# -----------------------------
# Build CNN Model
# -----------------------------
model = models.Sequential([
    layers.Input(shape=(224, 224, 3)),

    layers.Rescaling(1./255),

    layers.Conv2D(32, (3,3), activation="relu"),
    layers.MaxPooling2D(),

    layers.Conv2D(64, (3,3), activation="relu"),
    layers.MaxPooling2D(),

    layers.Conv2D(128, (3,3), activation="relu"),
    layers.MaxPooling2D(),

    layers.Flatten(),

    layers.Dense(128, activation="relu"),

    layers.Dropout(0.3),

    layers.Dense(len(class_names), activation="softmax")
])

# -----------------------------
# Compile Model
# -----------------------------
model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# -----------------------------
# Show Model Summary
# -----------------------------
model.summary()

# -----------------------------
# Train Model
# -----------------------------
history = model.fit(
    train_dataset,
    validation_data=val_dataset,
    epochs=10
)

# -----------------------------
# Create models folder
# -----------------------------
os.makedirs("models", exist_ok=True)

# -----------------------------
# Save Model
# -----------------------------
model.save("models/plant_disease_model.keras")

print("\n===================================")
print("✅ Model Trained Successfully!")
print("✅ Model saved in models folder.")
print("===================================")
