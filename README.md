# 🌾 Maroc Agri-Yield — MLOps Pipeline

[![CI/CD](https://github.com/anassbr1/maroc-agri-yield-mlops/actions/workflows/ci.yml/badge.svg)](https://github.com/anassbr1/maroc-agri-yield-mlops/actions/workflows/ci.yml)

Pipeline MLOps de bout en bout pour la prévision des rendements agricoles au Maroc (contexte Génération Green).

## Objectifs

- Prévoir les rendements agricoles à partir de données météo et historiques
- Démontrer un pipeline MLOps production-ready
- Couvrir le cycle de vie complet : ingestion → features → modèle → serving → monitoring

## Architecture

```text
[ Open-Meteo ]        [ data.gov.ma ]        [ Medias24 ]
        \                     |                     /
         \                    |                    /
          v                   v                   v
            [ Ingestion ETL - src/ingestion/ ]
                              |
                              v
                [ DVC - versioning des données ]
                              |
                              v
             [ Feature Engineering - src/features/ ]
                              |
                              v
            [ LightGBM + MLflow Tracking + Registry ]
                              |
                              v
                [ FastAPI + Docker - src/api/ ]
                              |
                              v
             [ GitHub Actions CI/CD + Evidently drift ]
```

## Stack technique

| Couche | Outils |
|---|---|
| Ingestion | Open-Meteo API, BeautifulSoup |
| Feature Engineering | pandas, NumPy |
| Modélisation | LightGBM, scikit-learn |
| Tracking | MLflow Tracking + Model Registry |
| Serving | FastAPI + Pydantic |
| Data Versioning | DVC |
| Conteneurisation | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Monitoring | Evidently AI |
| Qualité | ruff, pytest, pre-commit |

## Résultats

| Métrique | Valeur |
|---|---|
| Test RMSE | 5.52 |
| Test MAE | 2.80 |
| Test R2 | 0.85 |

Modèle : LightGBM entraîné sur 2010-2021 (split temporel 80/20).

## Structure du projet

```text
maroc-agri-yield-mlops/
├── data/
│   ├── raw/                 # Données brutes (DVC)
│   ├── interim/             # Nettoyage intermédiaire
│   └── processed/           # Features finales (DVC)
├── src/
│   ├── ingestion/           # ETL météo, rendements, prix
│   ├── features/            # Feature engineering
│   ├── models/              # Entraînement + registry
│   ├── api/                 # FastAPI (schemas + main)
│   └── monitoring/          # Evidently drift
├── docker/                  # Dockerfile + docker-compose
├── .github/workflows/       # CI/CD GitHub Actions
├── tests/                   # Tests pytest
├── mlruns/                  # Backend MLflow
├── requirements.txt
└── README.md
```

## Démarrage rapide

### Installation

```bash
git clone [https://github.com/anassbr1/maroc-agri-yield-mlops.git](https://github.com/anassbr1/maroc-agri-yield-mlops.git)
cd maroc-agri-yield-mlops
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Pipeline d'entraînement

```bash
python -m src.ingestion.fetch_meteo
python -m src.ingestion.fetch_rendements
python -m src.features.build_features
python -m src.models.train
python -m src.models.register_model
```

### MLflow UI

```bash
mlflow ui --backend-store-uri ./mlruns --port 5000
```

### API en local avec Docker

```bash
docker compose -f docker/docker-compose.yml up
curl http://localhost:8000/health
```

Exemple de prédiction :

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "temp_max_moy": 25.0,
    "temp_min_moy": 12.0,
    "precip_sum": 50.0,
    "humidite_moy": 70.0,
    "vent_max": 15.0,
    "precip_cumul_6m": 300.0,
    "temp_moy_3m": 20.0,
    "rendement_lag1": 20.0,
    "rendement_lag2": 19.0,
    "rendement_lag3": 21.0,
    "rendement_moy_3": 20.0,
    "rendement_std_3": 1.0,
    "rendement_moy_5": 20.0,
    "rendement_std_5": 1.5
  }'
```

### Monitoring du drift

```bash
python -m src.monitoring.drift
start reports/drift/drift_report.html
```

## Limites connues

Les rendements (data.gov.ma) sont nationaux alors que la météo (Open-Meteo) est régionale. La météo a donc été agrégée au niveau national pour aligner les deux sources. Une évolution serait d'obtenir des rendements régionaux pour permettre du forecasting par région.

## Auteur

Anass — [GitHub](https://github.com/anassbr1)