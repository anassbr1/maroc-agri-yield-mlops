"""Tests unitaires pour le module d'ingestion."""

from pathlib import Path

import pandas as pd
import pytest

METEO_PATH = Path("data/raw/meteo/meteo_maroc_2015_2024.csv")


def _skip_if_missing():
    if not METEO_PATH.exists():
        pytest.skip(f"Dataset absent (normal en CI sans DVC pull) : {METEO_PATH}")


def test_meteo_file_exists():
    _skip_if_missing()
    assert METEO_PATH.exists()


def test_meteo_columns():
    _skip_if_missing()
    df = pd.read_csv(METEO_PATH)
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
    _skip_if_missing()
    df = pd.read_csv(METEO_PATH)
    assert df["date"].notna().all(), "Dates nulles détectées"


def test_meteo_regions_count():
    _skip_if_missing()
    df = pd.read_csv(METEO_PATH)
    assert df["region"].nunique() == 5
