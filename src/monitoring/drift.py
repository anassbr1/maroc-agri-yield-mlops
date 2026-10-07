"""Détection de data drift avec Evidently AI."""

from pathlib import Path

import pandas as pd
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report
from loguru import logger

REFERENCE_PATH = Path("data/processed/features_agri.csv")
CURRENT_PATH = Path("data/processed/features_agri.csv")
OUTPUT_DIR = Path("reports/drift")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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


def main():
    logger.info("🔍 Chargement des données")

    reference = pd.read_csv(REFERENCE_PATH)[FEATURE_COLS]
    current = pd.read_csv(CURRENT_PATH)[FEATURE_COLS]

    reference = reference.sample(frac=0.7, random_state=42)
    current = current.sample(frac=0.3, random_state=42)

    logger.info(f"Reference : {reference.shape} | Current : {current.shape}")

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference, current_data=current)

    output_path = OUTPUT_DIR / "drift_report.html"
    report.save_html(str(output_path))

    logger.success(f"📄 Rapport : {output_path}")

    result = report.as_dict()
    for metric in result["metrics"]:
        if metric["metric"] == "DatasetDriftMetric":
            drift_detected = metric["result"]["dataset_drift"]
            share_drifted = metric["result"]["share_of_drifted_columns"]
            logger.info(f"Data drift détecté : {drift_detected}")
            logger.info(f"Share of drifted columns : {share_drifted:.2%}")


if __name__ == "__main__":
    main()
