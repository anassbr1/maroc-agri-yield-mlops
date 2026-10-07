from pydantic import BaseModel, ConfigDict, Field


class PredictionInput(BaseModel):
    temp_max_moy: float = Field(..., description="Température max moyenne")
    temp_min_moy: float
    precip_sum: float
    humidite_moy: float
    vent_max: float
    precip_cumul_6m: float
    temp_moy_3m: float
    rendement_lag1: float
    rendement_lag2: float
    rendement_lag3: float
    rendement_moy_3: float
    rendement_std_3: float
    rendement_moy_5: float
    rendement_std_5: float


class PredictionOutput(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    prediction: float
    model_name: str
    model_stage: str
