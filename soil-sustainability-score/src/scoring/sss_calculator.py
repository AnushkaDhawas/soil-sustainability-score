"""
Soil Sustainability Score (SSS) calculation engine.

This is the rule-based scoring core described in the project spec:

    SSS = (0.70 * Chemical Health Score) + (0.30 * Physical Health Score)

Categories:
    80-100  Highly Sustainable
    60-79   Moderately Sustainable
    40-59   Needs Improvement
    < 40    Unsustainable

This module intentionally has NO ML dependency — it is the ground-truth
label generator used later to train/validate Random Forest and XGBoost
models in src/models/.
"""

from dataclasses import dataclass


@dataclass
class SoilSample:
    ph: float
    organic_carbon: float   # OC, %
    nitrogen: float          # N, kg/ha
    phosphorus: float        # P, kg/ha
    potassium: float         # K, kg/ha
    ec: float                 # Electrical Conductivity, dS/m
    texture_score: float      # 0-100, derived from soil texture class


def chemical_health_score(sample: SoilSample) -> float:
    """
    Placeholder scoring logic for pH, OC, N, P, K, EC.
    TODO: replace with calibrated sub-indices per parameter
    (e.g. ideal ranges from Soil Health Card guidelines).
    """
    raise NotImplementedError("Define chemical sub-index scoring rules here.")


def physical_health_score(sample: SoilSample) -> float:
    """
    Placeholder scoring logic for texture / water-holding capacity.
    TODO: replace with calibrated sub-index.
    """
    raise NotImplementedError("Define physical sub-index scoring rules here.")


def calculate_sss(sample: SoilSample) -> dict:
    chemical = chemical_health_score(sample)
    physical = physical_health_score(sample)
    score = round(0.70 * chemical + 0.30 * physical, 2)

    if score >= 80:
        category = "Highly Sustainable"
    elif score >= 60:
        category = "Moderately Sustainable"
    elif score >= 40:
        category = "Needs Improvement"
    else:
        category = "Unsustainable"

    return {
        "chemical_health_score": chemical,
        "physical_health_score": physical,
        "sss": score,
        "category": category,
    }
