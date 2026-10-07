import os

import mlflow
from dotenv import load_dotenv
from loguru import logger
from mlflow.tracking import MlflowClient

load_dotenv()

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "agri-yield-forecasting")
MODEL_NAME = os.getenv("MLFLOW_MODEL_NAME", "agri_yield_model")


def main():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = MlflowClient()

    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        logger.error(f"Expérience '{EXPERIMENT_NAME}' introuvable")
        return

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.test_rmse ASC"],
        max_results=1,
    )

    if not runs:
        logger.error("Aucun run trouvé. Lance d'abord : python -m src.models.train")
        return

    best_run = runs[0]
    run_id = best_run.info.run_id
    rmse = best_run.data.metrics.get("test_rmse", "N/A")

    logger.info(f"Meilleur run : {run_id} (test_rmse={rmse})")

    model_uri = f"runs:/{run_id}/model"

    result = mlflow.register_model(model_uri=model_uri, name=MODEL_NAME)
    logger.success(f"Modèle enregistré : {MODEL_NAME} v{result.version}")

    client.transition_model_version_stage(
        name=MODEL_NAME,
        version=result.version,
        stage="Production",
        archive_existing_versions=True,
    )
    logger.success(f"Version {result.version} → Production")


if __name__ == "__main__":
    main()
