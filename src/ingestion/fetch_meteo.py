"""
Ingestion des données météo historiques pour les régions agricoles marocaines.
Source : Open-Meteo Archive API (https://archive-api.open-meteo.com)
"""

import time
from pathlib import Path

import pandas as pd
import requests
from loguru import logger

# --- Configuration ---
# Coordonnées des régions agricoles marocaines
REGIONS_MAROC = {
    "souss_massa": {"lat": 30.42, "lon": -9.60, "nom": "Souss-Massa (Agadir)"},
    "fes_meknes": {"lat": 33.89, "lon": -5.55, "nom": "Fès-Meknès"},
    "rabat_sale_kenitra": {"lat": 34.02, "lon": -6.83, "nom": "Rabat-Salé-Kénitra"},
    "beni_mellal_khenifra": {"lat": 32.34, "lon": -6.36, "nom": "Béni Mellal-Khénifra"},
    "casablanca_settat": {"lat": 33.57, "lon": -7.59, "nom": "Casablanca-Settat"},
    "oriental_berkane": {"lat": 34.92, "lon": -2.32, "nom": "Oriental (Berkane)"},
}

# Période historique
START_DATE = "2015-01-01"
END_DATE = "2024-12-31"

# Variables météo à récupérer (daily)
DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "relative_humidity_2m_mean",
    "wind_speed_10m_max",
]

# Dossier de sortie
OUTPUT_DIR = Path("data/raw/meteo")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def fetch_with_retry(url: str, params: dict, max_retries: int = 5) -> dict:
    """
    Appel HTTP avec retry automatique et backoff exponentiel.

    Si l'API renvoie 429 (Too Many Requests), on attend 2^attempt secondes
    avant de réessayer. C'est le pattern standard en production.
    """
    for attempt in range(max_retries):
        response = requests.get(url, params=params, timeout=60)

        if response.status_code == 429:
            wait = 2 ** (attempt + 1)  # 2, 4, 8, 16, 32 secondes
            logger.warning(
                f"⏸️  429 reçu, tentative {attempt + 1}/{max_retries}. " f"Attente de {wait}s..."
            )
            time.sleep(wait)
            continue

        response.raise_for_status()
        return response.json()

    raise RuntimeError(f"Échec après {max_retries} tentatives")


def fetch_region_meteo(region_key: str, region_info: dict) -> pd.DataFrame:
    """Récupère les données météo pour une région donnée."""
    logger.info(f"📡 Récupération météo : {region_info['nom']}")

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": region_info["lat"],
        "longitude": region_info["lon"],
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": ",".join(DAILY_VARIABLES),
        "timezone": "Africa/Casablanca",
    }

    data = fetch_with_retry(url, params)

    # Conversion en DataFrame
    df = pd.DataFrame(data["daily"])
    df["region"] = region_key
    df["region_nom"] = region_info["nom"]
    df["latitude"] = region_info["lat"]
    df["longitude"] = region_info["lon"]

    logger.success(f"✅ {region_info['nom']} : {len(df)} jours récupérés")
    return df


def main():
    """Fonction principale : boucle sur toutes les régions."""
    logger.info("🚀 Début de l'ingestion météo")

    all_data = []

    for region_key, region_info in REGIONS_MAROC.items():
        try:
            df = fetch_region_meteo(region_key, region_info)
            all_data.append(df)
            time.sleep(3)  # ⏱️ Pause de 3s pour respecter l'API
        except Exception as e:
            logger.error(f"❌ Erreur pour {region_key}: {e}")

    # Concaténation
    df_final = pd.concat(all_data, ignore_index=True)
    df_final = df_final.rename(columns={"time": "date"})

    # Sauvegarde
    output_path = OUTPUT_DIR / "meteo_maroc_2015_2024.csv"
    df_final.to_csv(output_path, index=False)

    logger.success(f"💾 Fichier sauvegardé : {output_path}")
    logger.info(f"📊 Total : {len(df_final)} lignes, {df_final['region'].nunique()} régions")


if __name__ == "__main__":
    main()
