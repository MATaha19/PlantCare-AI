import os
import cv2

IMAGE_PATH = r"C:\Users\Mohammed Taha\OneDrive\Documents\Simats\Computer Vision\PlantCare-AI\PlantVillage\Pepper__bell___Bacterial_spot\0d8421cd-eebc-4018-b591-12352dd970a7___JR_B.Spot 3234.JPG"
OUTPUT_PATH = "test_bell_pepper.mp4"

image = cv2.imread(IMAGE_PATH)

if image is None:
    raise FileNotFoundError(
        f"Could not load image: {IMAGE_PATH}"
    )

height, width = image.shape[:2]

fps = 10
duration_seconds = 5

fourcc = cv2.VideoWriter_fourcc(
    *"mp4v"
)

video = cv2.VideoWriter(
    OUTPUT_PATH,
    fourcc,
    fps,
    (width, height)
)

for _ in range(
    fps * duration_seconds
):
    video.write(image)

video.release()

print("Video created successfully:")
print(os.path.abspath(OUTPUT_PATH))