"""
Feature engineering pour le forecasting agri-yield & prix.
Une SEULE source de vérité pour les features (train + inference).
"""

from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger

INPUT_METEO = Path("data/raw/meteo/meteo_maroc_2015_2024.csv")
INPUT_RENDEMENTS = Path("data/raw/rendements/rendements_clean.csv")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def encode_cyclical(df: pd.DataFrame, col: str, period: int) -> pd.DataFrame:
    df[f"{col}_sin"] = np.sin(2 * np.pi * df[col] / period)
    df[f"{col}_cos"] = np.cos(2 * np.pi * df[col] / period)
    return df


def aggregate_meteo_national(meteo_agg: pd.DataFrame) -> pd.DataFrame:
    logger.info("🌍 Agrégation météo au niveau national")

    meteo_national = meteo_agg.groupby(["annee", "mois"], as_index=False).agg(
        {
            "temp_max_moy": "mean",
            "temp_min_moy": "mean",
            "precip_sum": "mean",
            "humidite_moy": "mean",
            "vent_max": "mean",
            "precip_cumul_3m": "mean",
            "precip_cumul_6m": "mean",
            "temp_moy_3m": "mean",
            "mois_sin": "first",
            "mois_cos": "first",
        }
    )

    logger.info(f"Météo nationale : {meteo_national.shape}")
    return meteo_national


def build_all_features() -> pd.DataFrame:
    logger.info("🔧 Début du feature engineering")

    meteo = pd.read_csv(INPUT_METEO, parse_dates=["date"])
    rendements = pd.read_csv(INPUT_RENDEMENTS)

    logger.info(f"Météo : {meteo.shape}, Rendements : {rendements.shape}")

    meteo["annee"] = meteo["date"].dt.year
    meteo["mois"] = meteo["date"].dt.month

    meteo_agg = (
        meteo.groupby(["region", "annee", "mois"])
        .agg(
            temp_max_moy=("temperature_2m_max", "mean"),
            temp_min_moy=("temperature_2m_min", "mean"),
            precip_sum=("precipitation_sum", "sum"),
            humidite_moy=("relative_humidity_2m_mean", "mean"),
            vent_max=("wind_speed_10m_max", "max"),
        )
        .reset_index()
    )

    logger.info(f"Météo agrégée : {meteo_agg.shape}")

    meteo_agg = encode_cyclical(meteo_agg, "mois", 12)

    meteo_agg = meteo_agg.sort_values(["region", "annee", "mois"])
    meteo_agg["precip_cumul_3m"] = meteo_agg.groupby("region")["precip_sum"].transform(
        lambda x: x.rolling(3, min_periods=1).sum()
    )
    meteo_agg["precip_cumul_6m"] = meteo_agg.groupby("region")["precip_sum"].transform(
        lambda x: x.rolling(6, min_periods=1).sum()
    )
    meteo_agg["temp_moy_3m"] = meteo_agg.groupby("region")["temp_max_moy"].transform(
        lambda x: x.rolling(3, min_periods=1).mean()
    )

    meteo_national = aggregate_meteo_national(meteo_agg)

    meteo_annuel = meteo_national.groupby("annee", as_index=False).agg(
        {
            "temp_max_moy": "mean",
            "temp_min_moy": "mean",
            "precip_sum": "sum",
            "humidite_moy": "mean",
            "vent_max": "max",
            "precip_cumul_6m": "max",
            "temp_moy_3m": "mean",
        }
    )

    logger.info(f"Météo agrégée en annuel : {meteo_annuel.shape}")

    df = rendements.merge(meteo_annuel, on="annee", how="inner")
    logger.info(f"Après fusion : {df.shape}")

    df = df.sort_values(["produit", "annee"])

    for lag in [1, 2, 3]:
        df[f"rendement_lag{lag}"] = df.groupby("produit")["rendement"].shift(lag)

    for w in [3, 5]:
        df[f"rendement_moy_{w}"] = df.groupby("produit")["rendement"].transform(
            lambda x, w=w: x.rolling(w, min_periods=1).mean()
        )
        df[f"rendement_std_{w}"] = df.groupby("produit")["rendement"].transform(
            lambda x, w=w: x.rolling(w, min_periods=1).std()
        )

    df = df.dropna(subset=["rendement_lag3"])

    logger.success(f"✅ Dataset final : {df.shape}")
    return df


def main():
    df = build_all_features()

    output_path = OUTPUT_DIR / "features_agri.csv"
    df.to_csv(output_path, index=False)

    logger.success(f"💾 Sauvegardé : {output_path}")
    logger.info(f"📊 Colonnes : {df.columns.tolist()}")


if __name__ == "__main__":
    main()
