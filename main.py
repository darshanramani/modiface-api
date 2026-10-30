from fastapi import FastAPI, UploadFile, File
import mediapipe as mp
from PIL import Image
from io import BytesIO
import numpy as np
from fastapi.responses import Response

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

app = FastAPI()

# Step 1: Locate the pretrained model
MODEL_PATH = "models/deeplabv3.tflite"

# Step 2: Configure MediaPipe
base_options = python.BaseOptions(
    model_asset_path=MODEL_PATH
)

options = vision.ImageSegmenterOptions(
    base_options=base_options,
    output_category_mask=True
)

# Step 3: Load the model
segmenter = vision.ImageSegmenter.create_from_options(options)


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/segment")
async def segment_image(file: UploadFile = File(...)):

    # Read uploaded image
    image_bytes = await file.read()

    # Decode image
    pil_image = Image.open(BytesIO(image_bytes)).convert("RGB")

    # Convert into NumPy array
    image_array = np.array(pil_image)

    # Create MediaPipe image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=image_array
    )

    # Run segmentation
    result = segmenter.segment(mp_image)

    # Extract category mask
    category_mask = result.category_mask.numpy_view().squeeze(-1)
    print("Mask shape:", category_mask.shape)
    print("Mask dtype:", category_mask.dtype)
    print(
        "Unique category values:",
        np.unique(category_mask, return_counts=True)
    )

    # Background = 0, foreground = 255
    PERSON_CLASS_ID = 15

    binary_mask = np.where(
        category_mask == PERSON_CLASS_ID,
        255,
        0
    ).astype(np.uint8)

    # Convert mask into PNG
    mask_image = Image.fromarray(binary_mask)

    buffer = BytesIO()
    mask_image.save(buffer, format="PNG")

    # Return PNG image
    return Response(
        content=buffer.getvalue(),
        media_type="image/png"
    )