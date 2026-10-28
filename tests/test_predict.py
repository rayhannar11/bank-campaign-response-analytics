"""
test_predict.py
Unit test untuk modul src/predict.py (predict_one dan predict_batch).
Test ini berjalan tanpa membutuhkan model nyata di disk, karena
model di-mock menggunakan pytest + monkeypatch.
Jalankan: python -m pytest tests/ -v
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.predict import predict_one, predict_batch
from src.feature_engineering import ALL_FEATURE_COLUMNS


# ---------------------------------------------------------------------------
# Data contoh yang valid
# ---------------------------------------------------------------------------

VALID_RECORD = {
    "age": 35,
    "job": "technician",
    "marital": "married",
    "education": "secondary",
    "default": "no",
    "balance": 1000,
    "housing": "yes",
    "loan": "no",
    "contact": "cellular",
    "day": 15,
    "month": "may",
    "campaign": 2,
    "pdays": -1,
    "previous": 0,
    "poutcome": "unknown",
}


def _make_mock_model(predict_val=0, proba_val=0.15):
    """Buat mock model yang mengembalikan prediksi dan probabilitas tetap."""
    model = MagicMock()
    model.predict.return_value = np.array([predict_val])
    model.predict_proba.return_value = np.array([[1 - proba_val, proba_val]])
    return model


# ---------------------------------------------------------------------------
# Test predict_one
# ---------------------------------------------------------------------------

class TestPredictOne:
    def test_returns_dict_with_required_keys(self, tmp_path):
        model_path = tmp_path / "model.joblib"
        mock_model = _make_mock_model(predict_val=0, proba_val=0.2)
        with patch("src.predict.joblib.load", return_value=mock_model), \
             patch("src.predict.Path.exists", return_value=True):
            result = predict_one(VALID_RECORD, model_path=model_path)
        assert "prediction" in result
        assert "probability_yes" in result
        assert "note" in result

    def test_prediction_yes_when_model_returns_1(self, tmp_path):
        model_path = tmp_path / "model.joblib"
        mock_model = _make_mock_model(predict_val=1, proba_val=0.75)
        with patch("src.predict.joblib.load", return_value=mock_model), \
             patch("src.predict.Path.exists", return_value=True):
            result = predict_one(VALID_RECORD, model_path=model_path)
        assert result["prediction"] == "yes"
        assert result["probability_yes"] == 0.75

    def test_prediction_no_when_model_returns_0(self, tmp_path):
        model_path = tmp_path / "model.joblib"
        mock_model = _make_mock_model(predict_val=0, proba_val=0.1)
        with patch("src.predict.joblib.load", return_value=mock_model), \
             patch("src.predict.Path.exists", return_value=True):
            result = predict_one(VALID_RECORD, model_path=model_path)
        assert result["prediction"] == "no"

    def test_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            predict_one(VALID_RECORD, model_path=tmp_path / "nonexistent.joblib")

    def test_raises_on_missing_column(self, tmp_path):
        incomplete = {k: v for k, v in VALID_RECORD.items() if k != "age"}
        with patch("src.predict.Path.exists", return_value=True):
            with pytest.raises(ValueError, match="Kolom hilang"):
                predict_one(incomplete, model_path=tmp_path / "dummy.joblib")

    def test_raises_on_invalid_numeric(self, tmp_path):
        bad_record = {**VALID_RECORD, "age": "bukan_angka"}
        with patch("src.predict.joblib.load", return_value=_make_mock_model()), \
             patch("src.predict.Path.exists", return_value=True):
            with pytest.raises(ValueError, match="harus bertipe angka"):
                predict_one(bad_record, model_path=tmp_path / "dummy.joblib")

    def test_duration_not_required(self):
        """'duration' bukan bagian dari ALL_FEATURE_COLUMNS – tidak perlu di-pass."""
        assert "duration" not in ALL_FEATURE_COLUMNS
        # VALID_RECORD sudah tidak mengandung 'duration'
        assert "duration" not in VALID_RECORD


# ---------------------------------------------------------------------------
# Test predict_batch
# ---------------------------------------------------------------------------

class TestPredictBatch:
    def test_returns_dataframe_with_prediction_columns(self, tmp_path):
        df = pd.DataFrame([VALID_RECORD, VALID_RECORD])
        model_path = tmp_path / "model.joblib"
        mock_model = _make_mock_model(predict_val=0, proba_val=0.2)
        mock_model.predict.return_value = np.array([0, 0])
        mock_model.predict_proba.return_value = np.array([[0.8, 0.2], [0.8, 0.2]])
        with patch("src.predict.joblib.load", return_value=mock_model), \
             patch("src.predict.Path.exists", return_value=True):
            result = predict_batch(df, model_path=model_path)
        assert "prediction" in result.columns
        assert "probability_yes" in result.columns
        assert len(result) == 2

    def test_raises_file_not_found(self, tmp_path):
        df = pd.DataFrame([VALID_RECORD])
        with pytest.raises(FileNotFoundError):
            predict_batch(df, model_path=tmp_path / "nonexistent.joblib")

    def test_raises_on_missing_columns(self, tmp_path):
        df = pd.DataFrame([{"age": 30}])  # kolom tidak lengkap
        with patch("src.predict.Path.exists", return_value=True):
            with pytest.raises(ValueError, match="Kolom hilang"):
                predict_batch(df, model_path=tmp_path / "dummy.joblib")

    def test_raises_on_invalid_numeric_value(self, tmp_path):
        df = pd.DataFrame([{**VALID_RECORD, "age": "bukan_angka"}])
        with patch("src.predict.Path.exists", return_value=True):
            with pytest.raises(ValueError, match="age"):
                predict_batch(df, model_path=tmp_path / "dummy.joblib")
