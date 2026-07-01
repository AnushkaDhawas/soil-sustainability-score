# Soil Sustainability Score Calculator

A data-driven system to assess soil health and generate a Soil Sustainability
Score (SSS) to support farmers, agriculture officers, and government
administrators in soil management decisions.

## Formula

```
SSS = (0.70 x Chemical Health Score) + (0.30 x Physical Health Score)
```

| Score   | Category               |
|---------|-------------------------|
| 80-100  | Highly Sustainable      |
| 60-79   | Moderately Sustainable  |
| 40-59   | Needs Improvement       |
| < 40    | Unsustainable           |

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Backend:** Flask
- **Database:** PostgreSQL + PostGIS
- **Analytics:** Python, Pandas, NumPy
- **ML:** Random Forest, XGBoost (CNN planned as future scope for satellite imagery)
- **GIS:** QGIS, GeoPandas
- **Visualization:** Plotly, Matplotlib

## Project Structure

```
soil-sustainability-score/
├── data/
│   ├── raw/              # Original, untouched soil datasets (Soil Health Card, lab reports)
│   └── processed/        # Cleaned/validated data ready for modeling
├── notebooks/            # Jupyter notebooks for EDA and model experimentation
├── src/
│   ├── scoring/          # Rule-based SSS calculation engine (chemical + physical scores)
│   ├── models/           # ML training/inference code (Random Forest, XGBoost)
│   ├── api/              # Flask app, routes, request/response handling
│   ├── gis/              # GeoPandas/PostGIS helpers for map visualization
│   └── utils/            # Shared helpers (data validation, config loading)
├── static/                # CSS/JS assets for the dashboard
│   ├── css/
│   └── js/
├── templates/             # Flask/Jinja2 HTML templates
├── tests/                 # Unit tests
├── docs/                  # Project documentation (this is where your PDF spec lives)
├── outputs/reports/        # Generated soil health reports
├── requirements.txt
├── .env.example
└── .gitignore
```

## Build Order (recommended)

1. **Data** — source or simulate a soil dataset (pH, OC, N, P, K, EC, texture) in `data/raw/`.
2. **Scoring engine** (`src/scoring/`) — implement the rule-based SSS formula in plain
   Python first. This becomes both a working v1 and the label generator for ML.
3. **API** (`src/api/`) — a minimal Flask endpoint that takes soil parameters and
   returns a score + category using the scoring engine.
4. **ML models** (`src/models/`) — train Random Forest and XGBoost on your dataset,
   compare against the rule-based scores.
5. **GIS + dashboard** — visualize village/district-level scores on a map.
6. **CNN (future scope)** — satellite imagery for erosion/degradation detection.

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # then fill in your DB credentials
```

## Running

```bash
flask run
```
