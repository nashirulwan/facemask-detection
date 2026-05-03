"""Singleton loader for face detector and mask classifier models.

Both models are loaded once at application startup and reused
across all requests to avoid repeated disk I/O.
"""

from __future__ import annotations

import cv2
from tensorflow.keras.models import load_model as keras_load_model

from app.core.config import FACE_PROTOTXT, FACE_WEIGHTS, MASK_MODEL_PATH

_face_net = None
_mask_model = None


def load_models() -> None:
    """Pre-load both networks into module-level singletons."""
    global _face_net, _mask_model

    print(f"[model_loader] Loading face detector from {FACE_WEIGHTS} ...")
    _face_net = cv2.dnn.readNet(str(FACE_WEIGHTS), str(FACE_PROTOTXT))

    print(f"[model_loader] Loading mask classifier from {MASK_MODEL_PATH} ...")
    _mask_model = keras_load_model(str(MASK_MODEL_PATH))

    print("[model_loader] All models loaded successfully.")


def get_face_net():
    """Return the pre-loaded SSD face detector."""
    if _face_net is None:
        raise RuntimeError("Face detector not loaded. Call load_models() first.")
    return _face_net


def get_mask_model():
    """Return the pre-loaded mask classifier."""
    if _mask_model is None:
        raise RuntimeError("Mask model not loaded. Call load_models() first.")
    return _mask_model
