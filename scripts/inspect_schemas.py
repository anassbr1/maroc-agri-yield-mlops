import pandas as pd

meteo = pd.read_csv("data/raw/meteo/meteo_maroc_2015_2024.csv")
rendements = pd.read_csv("data/raw/rendements/rendements_clean.csv")

print("=== MÉTÉO ===")
print("Colonnes :", meteo.columns.tolist())
print("Régions  :", meteo["region"].unique() if "region" in meteo.columns else "PAS DE REGION")
print(
    "Années   :",
    sorted(meteo["date"].str[:4].unique())[:3],
    "...",
    sorted(meteo["date"].str[:4].unique())[-3:],
)

print("\n=== RENDEMENTS ===")
print("Colonnes :", rendements.columns.tolist())
print("Années   :", sorted(rendements["annee"].unique()))
print("Pas de colonne region ?", "region" not in rendements.columns)
