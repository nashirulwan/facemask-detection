"""Face mask detection service.

Implements the full pipeline:
1. SSD face detection → bounding boxes
2. Per-face mask classification via the custom CNN
3. Annotation of the original image with results
"""

from __future__ import annotations

import base64
import time
from io import BytesIO

import cv2
import numpy as np
from PIL import Image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array

from app.core.config import (
    FACE_CONFIDENCE_THRESHOLD,
    FACE_NMS_THRESHOLD,
    IMAGE_INPUT_SIZE,
    IMAGE_FACE_CONFIDENCE_THRESHOLD,
    IMAGE_FACE_NMS_THRESHOLD,
    IMAGE_MIN_FACE_SIZE_PX,
    MIN_FACE_SIZE_PX,
    WEBCAM_FACE_CONFIDENCE_THRESHOLD,
    WEBCAM_FACE_NMS_THRESHOLD,
    WEBCAM_MIN_FACE_SIZE_PX,
)
from app.core.model_loader import get_face_net, get_mask_model
from app.schemas.prediction import FaceDetection, PredictionResponse


def _get_detection_profile(profile: str) -> dict[str, float | int]:
    if profile == "image":
        return {
            "confidence_threshold": IMAGE_FACE_CONFIDENCE_THRESHOLD,
            "nms_threshold": IMAGE_FACE_NMS_THRESHOLD,
            "min_face_size": IMAGE_MIN_FACE_SIZE_PX,
        }

    if profile == "webcam":
        return {
            "confidence_threshold": WEBCAM_FACE_CONFIDENCE_THRESHOLD,
            "nms_threshold": WEBCAM_FACE_NMS_THRESHOLD,
            "min_face_size": WEBCAM_MIN_FACE_SIZE_PX,
        }

    return {
        "confidence_threshold": FACE_CONFIDENCE_THRESHOLD,
        "nms_threshold": FACE_NMS_THRESHOLD,
        "min_face_size": MIN_FACE_SIZE_PX,
    }


def _should_keep_webcam_candidate(
    *,
    box: list[int],
    confidence: float,
    best_confidence: float,
    image_width: int,
    image_height: int,
) -> bool:
    start_x, start_y, box_width, box_height = box
    end_x = start_x + box_width
    end_y = start_y + box_height
    center_x = start_x + (box_width / 2)
    center_y = start_y + (box_height / 2)

    touches_right = end_x >= image_width - 4
    touches_left = start_x <= 4
    touches_bottom = end_y >= image_height - 4
    near_bottom_half = center_y > image_height * 0.62
    far_from_center = abs(center_x - (image_width / 2)) > image_width * 0.16
    much_weaker_than_best = confidence < best_confidence * 0.8

    # Reject partial false positives that hug the lower side of the frame.
    if touches_bottom and (touches_left or touches_right) and near_bottom_half and far_from_center:
        return False

    # Also reject weaker edge-heavy candidates if there is a much stronger face.
    if much_weaker_than_best and touches_bottom and near_bottom_half:
        return False

    return True


def _pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
    """Convert a PIL Image to a BGR OpenCV array."""
    rgb = np.array(pil_image.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def _cv2_to_base64(image: np.ndarray, quality: int = 90) -> str:
    """Encode a BGR OpenCV image as a base64 JPEG string."""
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    _, buffer = cv2.imencode(".jpg", image, encode_params)
    return base64.b64encode(buffer).decode("utf-8")


def process_image(pil_image: Image.Image, profile: str = "default") -> PredictionResponse:
    """Run the full detection + classification pipeline on one image.

    Parameters
    ----------
    pil_image:
        Input image as a PIL Image (any mode).

    Returns
    -------
    PredictionResponse with per-face detections and the annotated image.
    """
    start = time.perf_counter()

    image = _pil_to_cv2(pil_image)
    (h, w) = image.shape[:2]
    profile_settings = _get_detection_profile(profile)
    confidence_threshold = float(profile_settings["confidence_threshold"])
    nms_threshold = float(profile_settings["nms_threshold"])
    min_face_size = int(profile_settings["min_face_size"])

    face_net = get_face_net()
    mask_model = get_mask_model()

    # --- Step 1: SSD face detection -------------------------------------------
    blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300), (104.0, 177.0, 123.0))
    face_net.setInput(blob)
    detections_raw = face_net.forward()

    candidate_boxes: list[list[int]] = []
    candidate_confidences: list[float] = []
    for i in range(detections_raw.shape[2]):
        confidence = float(detections_raw[0, 0, i, 2])
        if confidence < confidence_threshold:
            continue

        box = detections_raw[0, 0, i, 3:7] * np.array([w, h, w, h])
        (start_x, start_y, end_x, end_y) = box.astype("int")
        start_x = max(0, start_x)
        start_y = max(0, start_y)
        end_x = min(w - 1, end_x)
        end_y = min(h - 1, end_y)

        box_width = end_x - start_x
        box_height = end_y - start_y
        if box_width < min_face_size or box_height < min_face_size:
            continue

        candidate_boxes.append([start_x, start_y, box_width, box_height])
        candidate_confidences.append(confidence)

    if not candidate_boxes:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return PredictionResponse(
            faces_detected=0,
            detections=[],
            annotated_image=_cv2_to_base64(image),
            processing_time_ms=round(elapsed_ms, 1),
        )

    picked_indices = cv2.dnn.NMSBoxes(
        candidate_boxes,
        candidate_confidences,
        confidence_threshold,
        nms_threshold,
    )

    if len(picked_indices) == 0:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return PredictionResponse(
            faces_detected=0,
            detections=[],
            annotated_image=_cv2_to_base64(image),
            processing_time_ms=round(elapsed_ms, 1),
        )

    results: list[FaceDetection] = []
    picked_flat = [int(idx) for idx in np.array(picked_indices).flatten()]
    best_confidence = max(candidate_confidences[int(idx)] for idx in picked_flat)

    for idx in picked_flat:
        if profile == "webcam" and not _should_keep_webcam_candidate(
            box=candidate_boxes[idx],
            confidence=candidate_confidences[idx],
            best_confidence=best_confidence,
            image_width=w,
            image_height=h,
        ):
            continue

        start_x, start_y, box_width, box_height = candidate_boxes[int(idx)]
        end_x = start_x + box_width
        end_y = start_y + box_height

        face = image[start_y:end_y, start_x:end_x]
        if face.size == 0:
            continue

        # --- Step 2: Mask classification --------------------------------------
        face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        face_resized = cv2.resize(face_rgb, (IMAGE_INPUT_SIZE, IMAGE_INPUT_SIZE))
        face_arr = img_to_array(face_resized)
        face_preprocessed = preprocess_input(face_arr)
        face_batch = np.expand_dims(face_preprocessed, axis=0)

        # Label map: ["with_mask", "without_mask"]
        # Index 0 = with_mask prob, Index 1 = without_mask prob
        (mask, without_mask) = mask_model.predict(face_batch, verbose=0)[0]

        label = "Mask" if mask > without_mask else "No Mask"
        score = float(max(mask, without_mask) * 100)
        color_bgr = (0, 255, 0) if label == "Mask" else (0, 0, 255)
        color_hex = "#10B981" if label == "Mask" else "#EF4444"

        # --- Step 3: Annotate -------------------------------------------------
        text = f"{label}: {score:.1f}%"
        cv2.putText(
            image, text,
            (start_x, start_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_bgr, 2,
        )
        cv2.rectangle(image, (start_x, start_y), (end_x, end_y), color_bgr, 2)

        results.append(FaceDetection(
            bbox=[int(start_x), int(start_y), int(end_x), int(end_y)],
            label=label,
            confidence=round(score, 2),
            color=color_hex,
        ))

    elapsed_ms = (time.perf_counter() - start) * 1000

    return PredictionResponse(
        faces_detected=len(results),
        detections=results,
        annotated_image=_cv2_to_base64(image),
        processing_time_ms=round(elapsed_ms, 1),
    )


def process_frame_bytes(frame_bytes: bytes, profile: str = "webcam") -> PredictionResponse:
    """Process raw JPEG/PNG bytes from a webcam frame.

    Returns the same structured response as image upload inference so the
    webcam client can reuse the same rendering path.
    """
    pil_image = Image.open(BytesIO(frame_bytes))
    return process_image(pil_image, profile=profile)
