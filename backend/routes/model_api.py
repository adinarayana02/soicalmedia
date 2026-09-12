from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import os
import json

router = APIRouter(prefix="/api/model")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

MODEL_WEIGHTS_PATH = os.path.join(MODELS_DIR, "behavior_model.pkl")
MODEL_METRICS_PATH = os.path.join(MODELS_DIR, "model_metrics.json")

@router.get("/metrics")
async def get_model_metrics():
    """
    Returns the performance metrics of the research-level behavior model.
    """
    if not os.path.exists(MODEL_METRICS_PATH):
        raise HTTPException(status_code=404, detail="Model metrics not found. Train the model first.")
        
    with open(MODEL_METRICS_PATH, "r") as f:
        metrics = json.load(f)
        
    return JSONResponse(content=metrics)

@router.get("/download")
async def download_model_weights():
    """
    Downloads the trained behavior_model.pkl weights file.
    """
    if not os.path.exists(MODEL_WEIGHTS_PATH):
        raise HTTPException(status_code=404, detail="Model weights not found. Train the model first.")
        
    return FileResponse(
        path=MODEL_WEIGHTS_PATH, 
        filename="behavior_model.pkl",
        media_type="application/octet-stream"
    )
