"""
Data loader for the Akola soil profile dataset provided by the project guide.

CONFIRMED FROM ACTUAL DATA:
- Each row is already ONE soil profile (not one row per horizon layer).
- Columns use Title Case exactly as below (pandas is case-sensitive).
- 'Horizon Sequence' values like 'Waterbody' and 'Habitation' mark
  non-agricultural land parcels included in the government survey — these
  rows have text placeholders in EVERY column (including N, P, K) and get
  dropped entirely.
- Real soil texture values found: 'Gravely Clay', 'Clay'.
- N, P, K are in kg/ha (values like 125.8, 17.4, 489.6 match standard
  Soil Health Card kg/ha ranges) — no unit conversion needed against the
  ranges already used in src/scoring/sss_calculator.py.
"""

import pandas as pd
from pathlib import Path

RAW_DATA_PATH = Path("data/raw/Akola_Soil Data (1).csv")
PROCESSED_DATA_PATH = Path("data/processed/akola_soil_clean.csv")

# Non-soil land-use labels found in 'Horizon Sequence' — these rows get dropped
NON_SOIL_LABELS = ["Waterbody", "Habitation"]

# Confirmed texture labels in this dataset. Score reflects general physical
# soil health / water-holding capacity — clay soils hold water well but can
# have drainage/aeration issues, gravelly clay is penalized further for
# poor water retention due to gravel content.
# TODO: revisit these two scores with your guide — they're reasonable
# defaults but not officially calibrated values.
TEXTURE_SCORE_MAP = {
    "clay": 65,
    "gravely clay": 45,
}

# Columns actually needed, using their REAL names from the CSV
COLUMNS_OF_INTEREST = [
    "FID", "Profile_No", "Horizon Sequence",
    "State", "District", "Block", "Village",
    "Texture", "Sand", "Silt", "Clay",
    "pH", "EC", "OC", "N", "P", "K",
]


def load_raw_data(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


def remove_non_soil_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows that represent waterbodies, habitation, or other
    non-agricultural land parcels rather than real soil profiles."""
    before = len(df)
    soil_df = df[~df["Horizon Sequence"].isin(NON_SOIL_LABELS)].copy()
    print(f"Dropped {before - len(soil_df)} non-soil rows "
          f"(waterbody/habitation) — {len(soil_df)} real soil profiles remain")
    return soil_df


def texture_to_score(texture_label: str) -> float:
    if not isinstance(texture_label, str):
        return 50.0  # neutral fallback for missing/unknown values
    key = texture_label.strip().lower()
    return TEXTURE_SCORE_MAP.get(key, 50.0)  # 50 = fallback for unmapped labels


def clean_and_prepare(df: pd.DataFrame) -> pd.DataFrame:
    df = df[COLUMNS_OF_INTEREST].copy()

    # Standardize column names to match SoilSample fields in sss_calculator.py
    df = df.rename(columns={
        "pH": "ph",
        "EC": "ec",
        "OC": "organic_carbon",
        "N": "nitrogen",
        "P": "phosphorus",
        "K": "potassium",
        "Texture": "texture",
    })

    # Convert N, P, K to numeric now that non-soil text rows are gone
    for col in ["nitrogen", "phosphorus", "potassium", "ph", "ec", "organic_carbon"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Derive texture_score from texture label
    df["texture_score"] = df["texture"].apply(texture_to_score)

    # Report missing values before dropping
    missing_report = df.isnull().sum()
    missing_report = missing_report[missing_report > 0]
    if len(missing_report) > 0:
        print("Missing values found:")
        print(missing_report)

    # Drop rows missing any of the core scoring parameters
    core_fields = ["ph", "ec", "organic_carbon", "nitrogen", "phosphorus",
                    "potassium", "texture_score"]
    before = len(df)
    df = df.dropna(subset=core_fields)
    print(f"Dropped {before - len(df)} rows with missing core parameters")

    return df


def main():
    raw = load_raw_data()
    soil_only = remove_non_soil_rows(raw)
    clean = clean_and_prepare(soil_only)

    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"Saved {len(clean)} clean rows to {PROCESSED_DATA_PATH}")
    print(clean.head())


if __name__ == "__main__":
    main()
