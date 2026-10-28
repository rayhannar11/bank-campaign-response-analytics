"""
test_feature_engineering.py
Unit test untuk modul src/feature_engineering.py.
Jalankan: python -m pytest tests/ -v
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.feature_engineering import (
    build_preprocessor,
    encode_target,
    ALL_FEATURE_COLUMNS,
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
)


@pytest.fixture
def sample_X():
    """DataFrame fitur minimal untuk pengujian pipeline preprocessing."""
    return pd.DataFrame({
        "age": [30, 45],
        "job": ["technician", "management"],
        "marital": ["single", "married"],
        "education": ["secondary", "tertiary"],
        "default": ["no", "no"],
        "balance": [1000, 2000],
        "housing": ["yes", "no"],
        "loan": ["no", "no"],
        "contact": ["cellular", "telephone"],
        "day": [15, 20],
        "month": ["may", "jun"],
        "campaign": [1, 3],
        "pdays": [-1, 90],
        "previous": [0, 2],
        "poutcome": ["unknown", "success"],
    })


class TestBuildPreprocessor:
    def test_returns_column_transformer(self, sample_X):
        from sklearn.compose import ColumnTransformer
        preprocessor = build_preprocessor()
        assert isinstance(preprocessor, ColumnTransformer)

    def test_fit_transform_returns_array(self, sample_X):
        preprocessor = build_preprocessor()
        result = preprocessor.fit_transform(sample_X)
        assert isinstance(result, np.ndarray)
        assert result.shape[0] == len(sample_X)

    def test_no_data_leakage_with_train_test(self, sample_X):
        """Preprocessor hanya boleh di-fit pada data training."""
        preprocessor = build_preprocessor()
        train = sample_X.iloc[:1]
        test = sample_X.iloc[1:]
        preprocessor.fit(train)
        # transform test tidak boleh raise (handle_unknown='ignore')
        result = preprocessor.transform(test)
        assert result.shape[0] == 1

    def test_handles_unknown_category(self, sample_X):
        """Kategori baru saat prediksi tidak boleh menyebabkan error."""
        preprocessor = build_preprocessor()
        preprocessor.fit(sample_X)
        new_data = sample_X.copy()
        new_data["job"] = "astronaut"  # kategori tidak ada di training
        result = preprocessor.transform(new_data)
        assert result.shape[0] == len(new_data)


class TestEncodeTarget:
    def test_yes_becomes_1(self):
        series = pd.Series(["yes", "no", "yes"])
        result = encode_target(series)
        assert list(result) == [1, 0, 1]

    def test_no_becomes_0(self):
        series = pd.Series(["no"])
        result = encode_target(series)
        assert result.iloc[0] == 0

    def test_output_is_int(self):
        series = pd.Series(["yes", "no"])
        result = encode_target(series)
        assert result.dtype == "int64"


class TestFeatureDefinitions:
    def test_no_duration_in_features(self):
        """duration harus tidak ada di fitur (data leakage)."""
        assert "duration" not in ALL_FEATURE_COLUMNS

    def test_no_target_in_features(self):
        assert "y" not in ALL_FEATURE_COLUMNS

    def test_numeric_categorical_disjoint(self):
        """Fitur numerik dan kategorikal tidak boleh tumpang tindih."""
        assert set(NUMERIC_FEATURES).isdisjoint(set(CATEGORICAL_FEATURES))

    def test_union_equals_all_features(self):
        assert sorted(NUMERIC_FEATURES + CATEGORICAL_FEATURES) == sorted(ALL_FEATURE_COLUMNS)
