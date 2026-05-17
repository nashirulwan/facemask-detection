"""Application configuration."""

from pathlib import Path

# Base paths
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BACKEND_DIR / "models"
EXPERIMENTS_DIR = MODELS_DIR / "experiments"

# Face detector (OpenCV DNN SSD)
FACE_PROTOTXT = MODELS_DIR / "deploy.prototxt.txt"
FACE_WEIGHTS = MODELS_DIR / "res10_300x300_ssd_iter_140000.caffemodel"

# Mask classifier
MASK_MODEL_PATH = MODELS_DIR / "face_mask_model.h5"

# Detection settings
FACE_CONFIDENCE_THRESHOLD = 0.3
FACE_NMS_THRESHOLD = 0.35
MIN_FACE_SIZE_PX = 48

# Profile-specific tuning
IMAGE_FACE_CONFIDENCE_THRESHOLD = 0.2
IMAGE_FACE_NMS_THRESHOLD = 0.3
IMAGE_MIN_FACE_SIZE_PX = 20

WEBCAM_FACE_CONFIDENCE_THRESHOLD = 0.5
WEBCAM_FACE_NMS_THRESHOLD = 0.3
WEBCAM_MIN_FACE_SIZE_PX = 72
IMAGE_INPUT_SIZE = 96  # model expects 96x96

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "*",
]
