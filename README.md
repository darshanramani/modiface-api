# Image Segmentation API — FastAPI, MediaPipe & Docker

A Python REST API that accepts an image and returns a PNG segmentation mask using the pretrained **MediaPipe DeepLab-v3** model. Built as an MLOps technical assessment to demonstrate model integration, API development, local inference, and containerization.

## Features

- **`POST /segment`** — Upload a JPEG or PNG image and receive a segmentation mask as a PNG response.
- **`GET /health`** — Lightweight endpoint to confirm the API is responding.
- **Pretrained model inference** — Uses a local DeepLab-v3 TensorFlow Lite (`.tflite`) model through MediaPipe Tasks.
- **In-memory image processing** — Uses Pillow, NumPy, and `BytesIO` to process and return images without writing temporary output files.
- **Docker support** — Includes a Dockerfile for running the service in a Linux container.
- **Interactive API documentation** — Available through FastAPI's Swagger UI at `/docs`.

## Technology Stack

| Component | Technology |
| --- | --- |
| Language | Python |
| API framework | FastAPI |
| ASGI server | Uvicorn |
| Segmentation | MediaPipe Image Segmenter with DeepLab-v3 |
| Image handling | Pillow, NumPy |
| Containerization | Docker |

## Project Structure

```text
modiface-segmentation-api/
├── main.py                  # FastAPI endpoints and segmentation logic
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container image definition
├── .dockerignore            # Files excluded from Docker build context
└── models/
    └── deeplabv3.tflite    # Pretrained model (download separately if omitted)
```

## Prerequisites

- Python **3.12** (the Docker image uses Python 3.12)
- pip
- Optional: Docker Desktop or another compatible Docker Engine

## Model Setup

The project uses the publicly available MediaPipe DeepLab-v3 model. From the project root, download it into `models/` before starting the API or building the Docker image.

**PowerShell:**

```powershell
New-Item -ItemType Directory -Force models | Out-Null
Invoke-WebRequest -Uri "https://storage.googleapis.com/mediapipe-models/image_segmenter/deeplab_v3/float32/1/deeplab_v3.tflite" -OutFile "models/deeplabv3.tflite"
```

If you already have the file in `models/`, skip this step. The model path expected by the application is `models/deeplabv3.tflite`.

## Run Locally

In Windows PowerShell, from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Once the server starts:

- Health check: http://127.0.0.1:8000/health
- Swagger UI: http://127.0.0.1:8000/docs

For Linux/macOS, activate the environment with `source .venv/bin/activate` instead.

## API Reference

### `GET /health`

Checks that the FastAPI application is responding.

**Example response (`200 OK`):**

```json
{"status": "ok"}
```

> A successful health response confirms the HTTP service is available; it does not independently measure segmentation accuracy.

### `POST /segment`

Uploads an image as a multipart form file and returns a **PNG segmentation mask**.

| Property | Value |
| --- | --- |
| HTTP method | `POST` |
| Path | `/segment` |
| Request body | `multipart/form-data` |
| Form field | `file` |
| Intended image formats | JPEG, PNG |
| Successful response | `200 OK`, `Content-Type: image/png` |

**Example request (PowerShell, using `curl.exe`):**

```powershell
curl.exe -X POST "http://127.0.0.1:8000/segment" -F "file=@person.jpg" --output mask.png
```

Replace `person.jpg` with the path to your test image. The response is saved as `mask.png`.

The output mask has the same width and height as the uploaded image. In the implementation developed for this assessment, the model's **person category (ID 15)** is represented as white (`255`) and other categories as black (`0`). Results depend on the pretrained model and input image; not every person or edge will be identified perfectly.

**Example using Swagger UI:**

1. Visit `/docs`.
2. Expand **POST /segment** and click **Try it out**.
3. Choose a JPEG or PNG image and click **Execute**.
4. Save or inspect the returned PNG response.

## Run with Docker

Ensure the model file exists under `models/`, then build the image from the project root:

```powershell
docker build -t modiface-segmentation-api .
```

If Docker's default build network cannot reach Debian package repositories, host networking may help **where supported and enabled**:

```powershell
docker build --network=host -t modiface-segmentation-api .
```

Run the container:

```powershell
docker run -d --name modiface-api -p 8001:8000 modiface-segmentation-api
```

Verify that it is running:

```powershell
docker ps
docker logs modiface-api
```

Access the containerized API:

- Health check: http://localhost:8001/health
- Swagger UI: http://localhost:8001/docs

**Port mapping:** `8001:8000` maps port `8001` on the host to the application's port `8000` inside the container.

**Container management:**

```powershell
docker stop modiface-api
docker start modiface-api
docker logs --tail 40 modiface-api
```

To recreate the container after rebuilding the image:

```powershell
docker rm -f modiface-api
docker run -d --name modiface-api -p 8001:8000 modiface-segmentation-api
```

## Basic Verification

The following manual checks were performed during development:

- Started the application locally with Uvicorn.
- Submitted an image to `POST /segment` and received a PNG response.
- Checked the mask array dimensions against the uploaded image dimensions.
- Built the Docker image and ran the application as a container.
- Confirmed that both `/health` and `/segment` respond from the container.

**Suggested submission checks:** Before sharing, confirm that an invalid or corrupted file produces an appropriate client error, that the input and output image dimensions match, and that segmentation quality is acceptable on several representative photographs. These additional checks should not be considered complete unless tested.

## Implementation Notes and Limitations

- Inference uses a **pretrained** model; no fine-tuning or training is included.
- DeepLab-v3 performs **semantic segmentation**, so output accuracy depends on the scene and model predictions.
- The category-to-mask conversion selects the model's person class (ID `15`).
- In the current design, the segmenter is initialized at application startup rather than loaded for every request.
- The `/health` endpoint is a basic liveness-style check, not a model quality test.
- Production deployments would additionally benefit from upload-size limits, robust image-content validation, structured logging, concurrency safeguards, automated tests, and security review.

## References

- [MediaPipe Image Segmenter — Python guide](https://ai.google.dev/edge/mediapipe/solutions/vision/image_segmenter/python)
- [MediaPipe image segmentation example notebook](https://colab.research.google.com/github/googlesamples/mediapipe/blob/main/examples/image_segmentation/python/image_segmentation.ipynb)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Docker documentation](https://docs.docker.com/)

## Submission Note

This repository was prepared for a technical assessment. Keep it **private** unless the organization explicitly authorizes public sharing. Do not commit proprietary instructions, confidential emails, API keys, or personal information.
