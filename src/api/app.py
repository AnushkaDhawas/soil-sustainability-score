"""
Flask entry point for the Soil Sustainability Score API.
Run with:  python app.py
"""
import sys
import os

# Allow imports from the project root (so "src.scoring..." works)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from flask import Flask, jsonify, request
from src.scoring.sss_calculator import SoilSample, calculate_sss

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


@app.route("/score", methods=["POST"])
def score():
    data = request.get_json()

    sample = SoilSample(
        ph=data["ph"],
        organic_carbon=data["organic_carbon"],
        nitrogen=data["nitrogen"],
        phosphorus=data["phosphorus"],
        potassium=data["potassium"],
        ec=data["ec"],
        texture_score=data["texture_score"],
    )

    result = calculate_sss(sample)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)