"""
Flask entry point for the Soil Sustainability Score API.

Run with:  flask run   (after setting FLASK_APP=src/api/app.py in .env)
"""

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


# TODO: add /score endpoint that accepts soil parameters (pH, OC, N, P, K, EC,
# texture) and returns the result of src.scoring.sss_calculator.calculate_sss


if __name__ == "__main__":
    app.run(debug=True)
