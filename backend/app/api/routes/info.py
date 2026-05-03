"""Model info routes — metadata about the loaded model and paper."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.prediction import ModelInfo

router = APIRouter(prefix="/api", tags=["info"])


@router.get("/model-info", response_model=ModelInfo)
async def get_model_info():
    """Return metadata about the deployed model and the reference paper."""
    return ModelInfo(
        paper_title="A real time face mask detection system using convolutional neural network",
        paper_doi="10.1007/s11042-022-12166-x",
        architecture=(
            "5× Conv2D(16→256) + MaxPool → Flatten → Dense(1024) → Dense(64) → Dense(2, softmax)"
        ),
        input_size=96,
        num_classes=2,
        class_labels=["with_mask", "without_mask"],
        face_detector="OpenCV DNN SSD (res10_300x300_ssd_iter_140000)",
    )


@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}
