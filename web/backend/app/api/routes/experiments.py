"""Experiment results routes — serves training metrics and plots."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.config import EXPERIMENTS_DIR
from app.schemas.prediction import ExperimentSummary

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


def _read_json(filename: str) -> dict | list:
    """Read a JSON file from the experiments directory."""
    path = EXPERIMENTS_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"{filename} not found")
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/summary", response_model=ExperimentSummary)
async def get_summary():
    """Return the training run summary."""
    return _read_json("run_summary.json")


@router.get("/classification-report")
async def get_classification_report():
    """Return the classification report as JSON."""
    return _read_json("classification_report.json")


@router.get("/confusion-matrix")
async def get_confusion_matrix():
    """Return the confusion matrix."""
    return _read_json("confusion_matrix.json")


@router.get("/history")
async def get_history():
    """Return per-epoch training history (loss, accuracy, val_loss, val_accuracy)."""
    return _read_json("history.json")


@router.get("/label-map")
async def get_label_map():
    """Return class label mapping."""
    return _read_json("label_map.json")


@router.get("/curves/{name}")
async def get_curve_image(name: str):
    """Serve accuracy or loss curve PNG.

    Valid names: 'accuracy_curve', 'loss_curve'
    """
    allowed = {"accuracy_curve", "loss_curve"}
    if name not in allowed:
        raise HTTPException(status_code=400, detail=f"Must be one of {allowed}")

    path = EXPERIMENTS_DIR / f"{name}.png"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"{name}.png not found")
    return FileResponse(path, media_type="image/png")
