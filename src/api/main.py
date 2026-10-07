import os
from contextlib import asynccontextmanager

import mlflow
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from loguru import logger

from src.api.schemas import PredictionInput, PredictionOutput

load_dotenv()

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_NAME = os.getenv("MLFLOW_MODEL_NAME", "agri_yield_model")
MODEL_STAGE = os.getenv("MLFLOW_MODEL_STAGE", "Production")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

model = None
model_uri = f"models:/{MODEL_NAME}/{MODEL_STAGE}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    logger.info(f"Chargement du modèle : {model_uri}")
    model = mlflow.pyfunc.load_model(model_uri)
    logger.success("Modèle chargé")
    yield
    logger.info("Arrêt de l'API")


app = FastAPI(
    title="Maroc Agri-Yield API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict", response_model=PredictionOutput)
def predict(payload: PredictionInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")

    input_df = pd.DataFrame([payload.model_dump()])
    prediction = model.predict(input_df)[0]

    return PredictionOutput(
        prediction=float(prediction),
        model_name=MODEL_NAME,
        model_stage=MODEL_STAGE,
    )
