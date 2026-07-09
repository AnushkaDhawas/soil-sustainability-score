"""
Flask entry point for the Soil Sustainability Score API.

Run with:  python src/api/app.py
"""

import sys
from pathlib import Path

# Allow importing sibling modules (src/scoring/) when running this file directly
sys.path.append(str(Path(__file__).resolve().parent.parent))

from flask import Flask, jsonify, request
from scoring.sss_calculator import SoilSample, calculate_sss
import joblib
import pandas as pd

app = Flask(__name__)

# --- Load trained ML models once at startup (not per-request) ---
MODEL_DIR = Path(__file__).resolve().parent.parent / "models" / "saved"
FEATURE_COLUMNS = [
    "ph", "ec", "organic_carbon", "nitrogen",
    "phosphorus", "potassium", "texture_score",
]

try:
    rf_model = joblib.load(MODEL_DIR / "random_forest_model.pkl")
    xgb_model = joblib.load(MODEL_DIR / "xgboost_model.pkl")
    label_encoder = joblib.load(MODEL_DIR / "label_encoder.pkl")
    MODELS_LOADED = True
except FileNotFoundError:
    # Models not trained/saved yet — /predict will return a clear error
    # instead of crashing the whole app on startup.
    rf_model = xgb_model = label_encoder = None
    MODELS_LOADED = False


REQUIRED_FIELDS = [
    "ph", "ec", "organic_carbon", "nitrogen",
    "phosphorus", "potassium", "texture_score",
]


def parse_soil_input(data):
    """Validate and convert request JSON into numeric soil parameters.
    Returns (values_dict, error_response) — error_response is None on success."""
    if data is None:
        return None, (jsonify({"error": "Request body must be valid JSON"}), 400)

    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        return None, (jsonify({
            "error": f"Missing required field(s): {', '.join(missing)}"
        }), 400)

    try:
        values = {field: float(data[field]) for field in REQUIRED_FIELDS}
    except (TypeError, ValueError):
        return None, (jsonify({
            "error": "All soil parameters must be numeric values"
        }), 400)

    return values, None


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


@app.route("/score", methods=["POST"])
def score_soil():
    """
    Accepts JSON soil parameters and returns the Soil Sustainability Score.

    Expected JSON body:
        {
            "ph": 6.8,
            "ec": 0.9,
            "organic_carbon": 0.55,
            "nitrogen": 150,
            "phosphorus": 20,
            "potassium": 300,
            "texture_score": 65
        }

    Returns:
        {
            "chemical_health_score": ...,
            "physical_health_score": ...,
            "sss": ...,
            "category": ...
        }
    """
    data = request.get_json(silent=True)
    values, error = parse_soil_input(data)
    if error:
        return error

    sample = SoilSample(**values)
    result = calculate_sss(sample)
    return jsonify(result), 200


@app.route("/predict", methods=["POST"])
def predict_soil():
    """
    Accepts the same JSON soil parameters as /score, but returns ML
    predictions from the trained Random Forest and XGBoost models
    alongside the rule-based score, for comparison.

    Returns:
        {
            "rule_based": { ...same as /score... },
            "random_forest_prediction": "Moderately Sustainable",
            "xgboost_prediction": "Moderately Sustainable"
        }
    """
    if not MODELS_LOADED:
        return jsonify({
            "error": "ML models not found. Run src/models/train_models.py "
                     "first to generate src/models/saved/*.pkl"
        }), 503

    data = request.get_json(silent=True)
    values, error = parse_soil_input(data)
    if error:
        return error

    # Rule-based score, for side-by-side comparison
    sample = SoilSample(**values)
    rule_based_result = calculate_sss(sample)

    # ML predictions — build a single-row DataFrame matching training feature order
    features_df = pd.DataFrame([[values[col] for col in FEATURE_COLUMNS]],
                                columns=FEATURE_COLUMNS)

    rf_pred_encoded = rf_model.predict(features_df)[0]
    xgb_pred_encoded = xgb_model.predict(features_df)[0]

    rf_pred_label = label_encoder.inverse_transform([rf_pred_encoded])[0]
    xgb_pred_label = label_encoder.inverse_transform([xgb_pred_encoded])[0]

    return jsonify({
        "rule_based": rule_based_result,
        "random_forest_prediction": rf_pred_label,
        "xgboost_prediction": xgb_pred_label,
    }), 200


if __name__ == "__main__":
    app.run(debug=True)