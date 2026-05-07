"""Prediction API routes — image upload and WebSocket streaming."""

from __future__ import annotations

import json

from fastapi import APIRouter, File, UploadFile, WebSocket, WebSocketDisconnect
from PIL import Image

from app.services.detector import process_frame_bytes, process_image

router = APIRouter(prefix="/api/predict", tags=["predict"])


@router.post("/image")
async def predict_image(file: UploadFile = File(...)):
    """Accept an uploaded image and return mask detection results.

    Returns JSON with per-face detections and the annotated image as base64.
    """
    pil_image = Image.open(file.file)
    result = process_image(pil_image)
    return result


@router.websocket("/stream")
async def predict_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time webcam frame processing.

    Client sends raw JPEG frame bytes.
    Server responds with JSON containing annotated_image (base64) and detections.
    """
    await websocket.accept()
    try:
        while True:
            frame_bytes = await websocket.receive_bytes()
            result = process_frame_bytes(frame_bytes)
            await websocket.send_text(json.dumps({
                "faces_detected": result.faces_detected,
                "annotated_image": result.annotated_image,
                "detections": [d.model_dump() for d in result.detections],
                "processing_time_ms": result.processing_time_ms,
            }))
    except WebSocketDisconnect:
        pass
