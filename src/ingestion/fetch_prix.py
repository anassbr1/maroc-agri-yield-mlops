"""
Scraping des prix de gros depuis Medias24.
Exemple : https://medias24.com/2026/03/11/marches-de-gros-de-casablanca-...
"""

import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger

OUTPUT_DIR = Path("data/raw/prix")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# URL d'exemple (à mettre à jour régulièrement)
URL = "https://medias24.com/2026/03/11/marches-de-gros-de-casablanca-prix-des-fruits-legumes-et-viandes-au-11-mars-2026-1641441/"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def scrape_prix(url: str) -> pd.DataFrame:
    """Scrape les prix depuis une page Medias24."""
    logger.info(f"🌐 Scraping : {url}")

    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "lxml")

    # Trouver le contenu principal
    article = soup.find("article") or soup.find("div", class_="post-content")
    text = article.get_text() if article else soup.get_text()

    # Regex pour extraire les prix (ex: "Tomate : entre 2,50 DH/kg et 4,50 DH/kg")
    pattern = r"([A-Za-zéèêàç\s\-]+)\s*:\s*entre\s*([\d,\.]+)\s*DH/kg\s*et\s*([\d,\.]+)\s*DH/kg"

    matches = re.findall(pattern, text)

    data = []
    for produit, prix_min, prix_max in matches:
        data.append(
            {
                "produit": produit.strip(),
                "prix_min_dh_kg": float(prix_min.replace(",", ".")),
                "prix_max_dh_kg": float(prix_max.replace(",", ".")),
                "date_scraping": datetime.now().strftime("%Y-%m-%d"),
                "source_url": url,
            }
        )

    df = pd.DataFrame(data)
    logger.success(f"✅ {len(df)} produits extraits")
    return df


def main():
    df = scrape_prix(URL)

    if df.empty:
        logger.warning("⚠️ Aucun prix extrait. La structure de la page a peut-être changé.")
        return

    output_path = OUTPUT_DIR / f"prix_{datetime.now().strftime('%Y%m%d')}.csv"
    df.to_csv(output_path, index=False)
    logger.success(f"💾 Sauvegardé : {output_path}")
    logger.info(f"\n{df.head(10)}")


if __name__ == "__main__":
    main()
