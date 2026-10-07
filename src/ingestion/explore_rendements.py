"""
Exploration du fichier de production végétale data.gov.ma.
Ce script nous aide à comprendre la structure AVANT de l'intégrer.
"""

from pathlib import Path

import pandas as pd

FILE_PATH = Path("data/raw/rendements/production_vegetale_2010_2022.xlsx")

# Lire le fichier Excel (toutes les feuilles)
xls = pd.ExcelFile(FILE_PATH)

print("📋 Feuilles disponibles :")
for sheet in xls.sheet_names:
    print(f"  - {sheet}")

# Lire la première feuille
df = pd.read_excel(FILE_PATH, sheet_name=0)
print("\n🔍 Aperçu :")
print(df.head(10))
print("\n📊 Colonnes :")
print(df.columns.tolist())
print("\n📈 Dimensions :", df.shape)
print("\n❓ Valeurs manquantes :")
print(df.isnull().sum())
