from pathlib import Path

import pandas as pd
from loguru import logger

INPUT_FILE = Path("data/raw/rendements/production_vegetale_2010_2022.xlsx")
OUTPUT_DIR = Path("data/raw/rendements")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_raw() -> pd.DataFrame:
    logger.info("📂 Chargement du fichier de rendements...")
    df = pd.read_excel(INPUT_FILE, sheet_name=0)
    df = df.dropna(how="all")

    # --- NORMALISATION DES COLONNES ---
    # strip() : enlève les espaces avant/après
    # lower() : met en minuscules
    # On remplace aussi les accents pour éviter les problèmes
    import unicodedata

    def clean_col(c: str) -> str:
        c = str(c).strip().lower()
        # Suppression des accents
        c = "".join(ch for ch in unicodedata.normalize("NFKD", c) if not unicodedata.combining(ch))
        # Remplace espaces et tirets par underscore
        c = c.replace(" ", "_").replace("-", "_")
        return c

    df.columns = [clean_col(c) for c in df.columns]

    logger.info(f"Brut : {df.shape}, colonnes normalisées : {df.columns.tolist()}")
    return df


def extract_year(occurrence: str) -> int:
    if pd.isna(occurrence):
        return None
    return int(str(occurrence).split("/")[0])


def reshape_to_wide(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Extraction de l'année
    df["annee"] = df["occurrence"].apply(extract_year)

    # 2. Normalisation des libellés d'indicateur
    indicateurs_uniques = df["indicateur"].unique().tolist()
    logger.info(f"Indicateurs détectés : {indicateurs_uniques}")

    def normalize(ind: str) -> str:
        ind_lower = str(ind).lower()
        if "production" in ind_lower:
            return "production"
        if "superficie" in ind_lower:
            return "superficie"
        return "autre"

    df["indicateur_norm"] = df["indicateur"].apply(normalize)
    df = df[df["indicateur_norm"].isin(["production", "superficie"])]

    # 3. Pivot
    df_wide = df.pivot_table(
        index=["annee", "filiere", "produit"],
        columns="indicateur_norm",
        values="valeur",
        aggfunc="sum",
    ).reset_index()

    df_wide.columns.name = None

    # 4. Rendement
    df_wide["rendement"] = df_wide["production"] / df_wide["superficie"].replace(0, pd.NA)

    before = len(df_wide)
    df_wide = df_wide.dropna(subset=["rendement", "production", "superficie"])
    logger.info(f"Lignes supprimées (rendement non calculable) : {before - len(df_wide)}")

    return df_wide


def main():
    df_raw = load_raw()
    df_wide = reshape_to_wide(df_raw)

    output_path = OUTPUT_DIR / "rendements_clean.csv"
    df_wide.to_csv(output_path, index=False)

    logger.success(f"💾 Sauvegardé : {output_path}")
    logger.info(f"📊 Dimensions finales : {df_wide.shape}")
    logger.info(f"📋 Colonnes : {df_wide.columns.tolist()}")
    logger.info(f"\n{df_wide.head(10)}")
    logger.info(f"\nAnnées disponibles : {sorted(df_wide['annee'].unique())}")
    logger.info(f"Produits uniques : {df_wide['produit'].nunique()}")
    logger.info(f"Filières : {df_wide['filiere'].unique().tolist()}")


if __name__ == "__main__":
    main()
