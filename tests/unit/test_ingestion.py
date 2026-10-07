"""Tests unitaires pour le module d'ingestion."""

from pathlib import Path

import pandas as pd

from src.ingestion.fetch_meteo import REGIONS_MAROC

# --- Tests sur les fichiers de données ---


def test_meteo_file_exists():
    """Vérifie que le fichier météo existe."""
    path = Path("data/raw/meteo/meteo_maroc_2015_2024.csv")
    assert path.exists(), f"Fichier manquant : {path}"


def test_meteo_columns():
    """Vérifie que les colonnes attendues sont présentes."""
    df = pd.read_csv("data/raw/meteo/meteo_maroc_2015_2024.csv")

    expected_cols = [
        "date",
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "region",
    ]
    for col in expected_cols:
        assert col in df.columns, f"Colonne manquante : {col}"


def test_meteo_no_null_dates():
    """Vérifie qu'il n'y a pas de dates nulles."""
    df = pd.read_csv("data/raw/meteo/meteo_maroc_2015_2024.csv")
    assert df["date"].notna().all(), "Dates nulles détectées"


def test_meteo_regions_count():
    """Vérifie qu'on a bien toutes les régions de REGIONS_MAROC dans le CSV."""
    df = pd.read_csv("data/raw/meteo/meteo_maroc_2015_2024.csv")

    expected = set(REGIONS_MAROC.keys())
    actual = set(df["region"].unique())

    assert actual == expected, (
        f"Régions manquantes : {expected - actual}. " f"Régions en trop : {actual - expected}."
    )


# --- Test sur la fonction d'ingestion elle-même (sans appel réseau) ---


def test_fetch_meteo_module_has_required_constants():
    """Vérifie que les constantes de configuration existent."""
    from src.ingestion import fetch_meteo

    assert hasattr(fetch_meteo, "REGIONS_MAROC")
    assert hasattr(fetch_meteo, "START_DATE")
    assert hasattr(fetch_meteo, "END_DATE")
    assert hasattr(fetch_meteo, "DAILY_VARIABLES")
    assert isinstance(fetch_meteo.REGIONS_MAROC, dict)
    assert len(fetch_meteo.REGIONS_MAROC) >= 5
