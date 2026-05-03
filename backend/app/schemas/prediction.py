"""Pydantic schemas for prediction API responses."""

from __future__ import annotations

from pydantic import BaseModel


class FaceDetection(BaseModel):
    """A single detected face with mask classification."""

    bbox: list[int]  # [x1, y1, x2, y2]
    label: str  # "Mask" or "No Mask"
    confidence: float  # 0-100 percentage
    color: str  # hex color for UI rendering


class PredictionResponse(BaseModel):
    """Full response for an image prediction request."""

    faces_detected: int
    detections: list[FaceDetection]
    annotated_image: str  # base64-encoded JPEG
    processing_time_ms: float


class ExperimentSummary(BaseModel):
    """Training run summary."""

    dataset_dir: str
    num_images: int
    train_samples: int
    test_samples: int
    epochs: int
    batch_size: int
    learning_rate: float
    seed: int
    final_train_accuracy: float
    final_val_accuracy: float
    test_accuracy: float


class ModelInfo(BaseModel):
    """Metadata about the loaded model and paper."""

    paper_title: str
    paper_doi: str
    architecture: str
    input_size: int
    num_classes: int
    class_labels: list[str]
    face_detector: str
