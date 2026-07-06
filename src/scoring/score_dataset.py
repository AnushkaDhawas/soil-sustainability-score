"""
Apply the rule-based SSS scoring engine to every cleaned soil profile,
and save the scored dataset. This is what will later be used as ground-truth
labels for training Random Forest / XGBoost models.

Run with: python src/scoring/score_dataset.py
"""

import pandas as pd
from pathlib import Path

from sss_calculator import SoilSample, calculate_sss

CLEAN_DATA_PATH = Path("data/processed/akola_soil_clean.csv")
SCORED_DATA_PATH = Path("data/processed/akola_soil_scored.csv")


def main():
    df = pd.read_csv(CLEAN_DATA_PATH)
    print(f"Loaded {len(df)} cleaned soil profiles")

    results = []
    for _, row in df.iterrows():
        sample = SoilSample(
            ph=row["ph"],
            organic_carbon=row["organic_carbon"],
            nitrogen=row["nitrogen"],
            phosphorus=row["phosphorus"],
            potassium=row["potassium"],
            ec=row["ec"],
            texture_score=row["texture_score"],
        )
        result = calculate_sss(sample)
        results.append(result)

    scored_df = pd.concat([df.reset_index(drop=True), pd.DataFrame(results)], axis=1)

    SCORED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    scored_df.to_csv(SCORED_DATA_PATH, index=False)
    print(f"Saved {len(scored_df)} scored profiles to {SCORED_DATA_PATH}")

    print("\n--- Score distribution ---")
    print(scored_df["category"].value_counts())
    print("\n--- SSS summary stats ---")
    print(scored_df["sss"].describe())


if __name__ == "__main__":
    main()
