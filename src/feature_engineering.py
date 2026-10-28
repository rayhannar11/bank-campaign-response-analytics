"""
feature_engineering.py
Pipeline preprocessing dan rekayasa fitur untuk model machine learning.
Digunakan oleh notebook 03 dan src/predict.py.
"""

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# ---------------------------------------------------------------------------
# Definisi fitur
# ---------------------------------------------------------------------------

# `duration` is excluded because it is only known after the call.
LEAKAGE_COLUMNS = ["duration"]

ALL_FEATURE_COLUMNS = [
    "age", "job", "marital", "education", "default", "balance", "housing", "loan",
    "contact", "day", "month", "campaign", "pdays", "previous", "poutcome",
]

NUMERIC_FEATURES = ["age", "balance", "day", "campaign", "pdays", "previous"]
CATEGORICAL_FEATURES = [c for c in ALL_FEATURE_COLUMNS if c not in NUMERIC_FEATURES]


def build_preprocessor() -> ColumnTransformer:
    """Bangun ColumnTransformer yang menangani fitur numerik dan kategorikal.

    Numeric features use median imputation and standard scaling.
    Categorical features use mode imputation and one-hot encoding.

    Preprocessing hanya boleh di-fit pada data training untuk mencegah
    information leakage into evaluation data.

    Returns:
        ColumnTransformer yang belum di-fit.
    """
    numeric_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def encode_target(series) -> "pd.Series":
    """Encode target 'yes'/'no' menjadi 1/0.

    Args:
        series: pd.Series dengan nilai 'yes' atau 'no'.

    Returns:
        pd.Series dengan nilai 0 atau 1 (int64).
    """
    return series.map({"no": 0, "yes": 1}).astype("int64")
