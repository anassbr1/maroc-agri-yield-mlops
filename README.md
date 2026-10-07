# 🌾 Maroc Agri-Yield & Market Price Forecasting — MLOps Pipeline

[![CI/CD](https://github.com/anassbr1/maroc-agri-yield-mlops/actions/workflows/ci.yml/badge.svg)](https://github.com/anassbr1/maroc-agri-yield-mlops/actions/workflows/ci.yml)

Pipeline MLOps de bout en bout pour la prévision des rendements agricoles au Maroc (contexte Génération Green), de l'ingestion jusqu'à la mise en production.

## 🎯 Objectifs

- Prévoir les rendements agricoles à partir de données météo et historiques
- Démontrer un pipeline MLOps production-ready
- Mettre en oeuvre le cycle de vie complet : ingestion → features → modèle → serving → monitoring

## 🏗️ Architecture
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ Open-Meteo │ │ data.gov.ma │ │ Medias24 │
│ (météo) │ │ (rendements) │ │ (prix) │
└───────┬────────┘ └───────┬────────┘ └───────┬────────┘
│ │ │
└────────────┬───────┴────────┬───────────┘
▼ ▼
┌──────────────────────────────┐
│ DVC (versioning données) │
└──────────────┬───────────────┘
▼
┌──────────────────────────────┐
│ Feature Engineering │
│ (lags, rolling, cyclique) │
└──────────────┬───────────────┘
▼
┌──────────────────────────────┐
│ LightGBM + MLflow Tracking │
│ + Model Registry │
└──────────────┬───────────────┘
▼
┌──────────────────────────────┐
│ FastAPI + Docker │
│ /predict /health │
└──────────────┬───────────────┘
▼
┌──────────────────────────────┐
│ GitHub Actions CI/CD │
│ + Evidently (drift) │
└──────────────────────────────┘

text

## 🛠️ Stack technique

| Couche | Outils |
|---|---|
| Ingestion | Open-Meteo API, BeautifulSoup |
| Feature Engineering | pandas, NumPy |
| Modélisation | LightGBM, scikit-learn |
| Tracking | MLflow (Tracking + Model Registry) |
| Serving | FastAPI + Pydantic |
| Data Versioning | DVC |
| Conteneurisation | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Monitoring | Evidently AI |
| Qualité | ruff, pytest, pre-commit |

## 📊 Résultats

| Métrique | Valeur |
|---|---|
| Test RMSE | ~5.51 |
| Test MAE | ~2.8 |
| Test R² | ~0.85 |

Modèle : LightGBM, entraîné sur 2010-2021 (split temporel 80/20).

## 🚀 Démarrage rapide

### Prérequis

- Python 3.10+
- Git
- DVC
- Docker Desktop

### Installation

```bash
git clone https://github.com/anassbr1/maroc-agri-yield-mlops.git
cd maroc-agri-yield-mlops
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
dvc pull
Entraîner le modèle
bash
python -m src.features.build_features
python -m src.models.train
python -m src.models.register_model
Lancer MLflow UI
bash
mlflow ui --backend-store-uri ./mlruns --port 5000
Ouvrir http://localhost:5000 pour visualiser les runs et le Model Registry.

Lancer l'API
bash
docker compose -f docker/docker-compose.yml up
Tester :

bash
curl http://localhost:8000/health
Détecter le drift
bash
python -m src.monitoring.drift
start reports/drift/drift_report.html
📁 Structure du projet
text
maroc-agri-yield-mlops/
├── data/                  # Données versionnées DVC (raw, interim, processed)
├── src/
│   ├── ingestion/         # ETL météo, rendements, prix
│   ├── features/          # Feature engineering
│   ├── models/            # Entraînement + registry
│   ├── api/               # FastAPI service
│   └── monitoring/        # Evidently drift detection
├── docker/                # Dockerfile + docker-compose
├── .github/workflows/     # CI/CD GitHub Actions
├── tests/                 # Tests unitaires pytest
├── mlruns/                # Backend MLflow
└── reports/               # Rapports de drift
⚠️ Limites connues
Les rendements proviennent de data.gov.ma à l'échelle nationale, alors que la météo (Open-Meteo) est régionale. Pour aligner les deux sources, la météo a été agrégée au niveau national.

Évolution future : obtenir des rendements régionaux pour permettre du forecasting par région.

🗺️ Roadmap
☑ Phase 0 : Fondations (setup, structure, DVC)
☑ Phase 1 : Data ingestion (météo + rendements + prix)
☑ Phase 2 : Feature engineering & modélisation
☑ Phase 3 : API FastAPI + Docker
☑ Phase 4 : CI/CD + monitoring drift
👤 Auteur
Anass — GitHub

text

---

## 📋 Commandes à exécuter (copie-colle bloc par bloc)

### Bloc 1 — Stage + commit + push

```powershell
git add .
git commit -m "docs: finalize README with architecture and results" --no-verify
git push
Sortie attendue du push :

text
To https://github.com/anassbr1/maroc-agri-yield-mlops.git
   xxxx..yyyy  main -> main
Bloc 2 — Vérification
powershell
git log --oneline -3
Tu dois voir tes 3 derniers commits, avec le nouveau en haut.
