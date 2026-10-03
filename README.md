# 🌾 Maroc Agri-Yield & Market Price Forecasting — MLOps Pipeline

> Pipeline MLOps de bout en bout pour la prévision des rendements agricoles
> et des prix de marché au Maroc (contexte Génération Green).

## 🎯 Objectifs

* Prévoir les rendements agricoles par région (Souss-Massa, Fès-Meknès, ...)
* Prévoir les prix de gros des fruits et légumes
* Démontrer un pipeline MLOps production-ready (ingestion → serving)

## 🏗️ Architecture

[Schéma à venir en Phase 1]

## 🛠️ Stack Technique

| Couche              | Outils                          |
| ------------------- | ------------------------------- |
| Ingestion           | Open-Meteo API, BeautifulSoup   |
| Feature Engineering | Polars / Pandas                 |
| Modélisation        | LightGBM, XGBoost, scikit-learn |
| Tracking            | MLflow                          |
| Serving             | FastAPI + Pydantic              |
| Data Versioning     | DVC                             |
| Conteneurisation    | Docker + Docker Compose         |
| CI/CD               | GitHub Actions                  |
| Monitoring          | Evidently AI                    |
| Qualité             | ruff, pytest, pre-commit        |

## 🚀 Démarrage rapide

### Prérequis

* Python 3.10+
* Git
* DVC

### Installation

```bash
git clone https://github.com/TON_USERNAME/maroc-agri-yield-mlops.git
cd maroc-agri-yield-mlops
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
dvc pull
```

## 📁 Structure du projet

[Voir arborescence]

## 📊 Résultats

[À remplir en Phase 2]

## 🗺️ Roadmap

* ☑ Phase 0 : Fondations (setup, structure, DVC)
* □ Phase 1 : Data ingestion (météo + prix)
* □ Phase 2 : Feature engineering & modélisation
* □ Phase 3 : API FastAPI + Docker
* □ Phase 4 : CI/CD + monitoring

## 👤 Auteur

Ton Nom — [LinkedIn](https://.../) — [GitHub](https://.../)
