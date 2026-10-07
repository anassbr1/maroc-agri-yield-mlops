"""
Entraînement du modèle de prévision agri-yield avec MLflow Tracking.
"""

import os
from pathlib import Path

import mlflow
import mlflow.lightgbm
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from lightgbm import LGBMRegressor
from loguru import logger
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

load_dotenv()

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "agri-yield-forecasting")

INPUT_FEATURES = Path("data/processed/features_agri.csv")

FEATURE_COLS = [
    "temp_max_moy",
    "temp_min_moy",
    "precip_sum",
    "humidite_moy",
    "vent_max",
    "precip_cumul_6m",
    "temp_moy_3m",
    "rendement_lag1",
    "rendement_lag2",
    "rendement_lag3",
    "rendement_moy_3",
    "rendement_std_3",
    "rendement_moy_5",
    "rendement_std_5",
]

TARGET_COL = "rendement"


def time_series_split(df: pd.DataFrame, test_size: float = 0.2):
    df = df.sort_values("annee")
    n = len(df)
    split_idx = int(n * (1 - test_size))

    train = df.iloc[:split_idx]
    test = df.iloc[split_idx:]

    logger.info(f"Train : {len(train)} lignes ({train['annee'].min()}-{train['annee'].max()})")
    logger.info(f"Test  : {len(test)} lignes ({test['annee'].min()}-{test['annee'].max()})")

    return train, test


def evaluate(y_true, y_pred) -> dict:
    return {
        "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
        "mae": mean_absolute_error(y_true, y_pred),
        "r2": r2_score(y_true, y_pred),
    }


def train_model(params: dict) -> dict:
    df = pd.read_csv(INPUT_FEATURES)

    train_df, test_df = time_series_split(df, test_size=0.2)

    x_train = train_df[FEATURE_COLS]
    y_train = train_df[TARGET_COL]
    x_test = test_df[FEATURE_COLS]
    y_test = test_df[TARGET_COL]

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run(run_name=f"lgbm_{params['n_estimators']}trees"):
        mlflow.log_params(params)

        model = LGBMRegressor(**params, random_state=42)
        model.fit(x_train, y_train)

        y_pred_train = model.predict(x_train)
        y_pred_test = model.predict(x_test)

        train_metrics = evaluate(y_train, y_pred_train)
        test_metrics = evaluate(y_test, y_pred_test)

        mlflow.log_metrics({f"train_{k}": v for k, v in train_metrics.items()})
        mlflow.log_metrics({f"test_{k}": v for k, v in test_metrics.items()})

        logger.info(f"Train RMSE : {train_metrics['rmse']:.4f}")
        logger.info(f"Test  RMSE : {test_metrics['rmse']:.4f}")

        mlflow.lightgbm.log_model(model, "model")

        importance = pd.DataFrame(
            {
                "feature": FEATURE_COLS,
                "importance": model.feature_importances_,
            }
        ).sort_values("importance", ascending=False)

        logger.info(f"\nTop 5 features :\n{importance.head()}")

        return test_metrics


def main():
    param_grid = [
        {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 5},
        {"n_estimators": 300, "learning_rate": 0.05, "max_depth": 7},
        {"n_estimators": 500, "learning_rate": 0.03, "max_depth": 9},
    ]

    results = []
    for params in param_grid:
        logger.info(f"🚀 Run avec {params}")
        metrics = train_model(params)
        results.append({"params": params, **metrics})

    best = min(results, key=lambda x: x["rmse"])
    logger.success(f"🏆 Meilleur : {best}")


if __name__ == "__main__":
    main()
