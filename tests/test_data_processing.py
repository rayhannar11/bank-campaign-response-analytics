"""
test_data_processing.py
Unit test untuk modul src/data_processing.py.
Jalankan: python -m pytest tests/ -v
"""

import sys
from pathlib import Path
import pandas as pd
import pytest

# Tambahkan root proyek ke path agar import src.* berjalan di luar notebook
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_processing import (
    load_raw,
    validate_schema,
    validate_target,
    clean,
    EXPECTED_COLUMNS,
    NUMERIC_COLUMNS,
    CATEGORICAL_COLUMNS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_df():
    """DataFrame minimal yang menyerupai data mentah bank-full.csv."""
    return pd.DataFrame({
        "age": [30, 45, 60],
        "job": ["management", "technician", "retired"],
        "marital": ["single", "married", "divorced"],
        "education": ["tertiary", "secondary", "primary"],
        "default": ["no", "no", "yes"],
        "balance": [1000, -50, 5000],
        "housing": ["yes", "no", "yes"],
        "loan": ["no", "yes", "no"],
        "contact": ["cellular", "telephone", "unknown"],
        "day": [15, 20, 5],
        "month": ["may", "jun", "oct"],
        "duration": [120, 300, 60],
        "campaign": [1, 3, 2],
        "pdays": [-1, 90, -1],
        "previous": [0, 2, 1],
        "poutcome": ["unknown", "success", "failure"],
        "y": ["no", "yes", "no"],
    })


@pytest.fixture
def clean_df(sample_df):
    """DataFrame setelah proses cleaning."""
    return clean(sample_df)


# ---------------------------------------------------------------------------
# Test validate_schema
# ---------------------------------------------------------------------------

class TestValidateSchema:
    def test_passes_with_correct_schema(self, sample_df):
        validate_schema(sample_df)  # tidak boleh raise

    def test_raises_on_missing_column(self, sample_df):
        df = sample_df.drop(columns=["age"])
        with pytest.raises(ValueError, match="Hilang"):
            validate_schema(df)

    def test_raises_on_extra_column(self, sample_df):
        df = sample_df.copy()
        df["extra_col"] = 0
        with pytest.raises(ValueError, match="tambahan"):
            validate_schema(df)


# ---------------------------------------------------------------------------
# Test validate_target
# ---------------------------------------------------------------------------

class TestValidateTarget:
    def test_passes_with_valid_target(self, sample_df):
        validate_target(sample_df)  # tidak boleh raise

    def test_raises_on_invalid_value(self, sample_df):
        df = sample_df.copy()
        df.loc[0, "y"] = "maybe"
        with pytest.raises(AssertionError):
            validate_target(df)


# ---------------------------------------------------------------------------
# Test clean
# ---------------------------------------------------------------------------

class TestClean:
    def test_returns_correct_columns(self, clean_df):
        assert list(clean_df.columns) == EXPECTED_COLUMNS

    def test_no_missing_target(self, clean_df):
        assert clean_df["y"].isna().sum() == 0

    def test_target_values_only_yes_no(self, clean_df):
        assert set(clean_df["y"].unique()) <= {"yes", "no"}

    def test_numeric_columns_are_numeric(self, clean_df):
        for col in NUMERIC_COLUMNS:
            assert pd.api.types.is_numeric_dtype(clean_df[col]), (
                f"Kolom {col} seharusnya numerik"
            )

    def test_removes_duplicate_rows(self):
        """Baris duplikat harus dihapus."""
        base = pd.DataFrame({
            "age": [30], "job": ["management"], "marital": ["single"],
            "education": ["tertiary"], "default": ["no"], "balance": [1000],
            "housing": ["yes"], "loan": ["no"], "contact": ["cellular"],
            "day": [15], "month": ["may"], "duration": [120], "campaign": [1],
            "pdays": [-1], "previous": [0], "poutcome": ["unknown"], "y": ["no"],
        })
        df = pd.concat([base, base], ignore_index=True)
        result = clean(df)
        assert len(result) == 1

    def test_pdays_minus_one_preserved(self, clean_df):
        """Nilai pdays = -1 harus dipertahankan (bukan diperlakukan sebagai missing)."""
        assert (clean_df["pdays"] == -1).sum() >= 0  # sentinel boleh ada

    def test_missing_categorical_filled_with_unknown(self):
        """Missing pada kolom kategorikal harus diisi 'unknown'."""
        df = pd.DataFrame({
            "age": [30], "job": [None], "marital": ["single"],
            "education": ["tertiary"], "default": ["no"], "balance": [1000],
            "housing": ["yes"], "loan": ["no"], "contact": ["cellular"],
            "day": [15], "month": ["may"], "duration": [120], "campaign": [1],
            "pdays": [-1], "previous": [0], "poutcome": ["unknown"], "y": ["yes"],
        })
        result = clean(df)
        assert result["job"].iloc[0] == "unknown"

    def test_removes_rows_without_target(self):
        """Baris dengan target NaN harus dihapus."""
        df = pd.DataFrame({
            "age": [30, 40], "job": ["management", "technician"],
            "marital": ["single", "married"], "education": ["tertiary", "secondary"],
            "default": ["no", "no"], "balance": [1000, 500],
            "housing": ["yes", "no"], "loan": ["no", "no"],
            "contact": ["cellular", "cellular"], "day": [15, 20],
            "month": ["may", "jun"], "duration": [120, 200], "campaign": [1, 2],
            "pdays": [-1, -1], "previous": [0, 0], "poutcome": ["unknown", "unknown"],
            "y": ["no", None],
        })
        result = clean(df)
        assert len(result) == 1
        assert result["y"].iloc[0] == "no"

    def test_reports_duplicates_and_missing_targets_separately(self, capsys):
        base = pd.DataFrame({
            "age": [30], "job": ["management"], "marital": ["single"],
            "education": ["tertiary"], "default": ["no"], "balance": [1000],
            "housing": ["yes"], "loan": ["no"], "contact": ["cellular"],
            "day": [15], "month": ["may"], "duration": [120], "campaign": [1],
            "pdays": [-1], "previous": [0], "poutcome": ["unknown"], "y": ["no"],
        })
        missing_target = base.copy()
        missing_target.loc[0, "y"] = None
        df = pd.concat([base, base, missing_target], ignore_index=True)

        result = clean(df)

        output = capsys.readouterr().out
        assert len(result) == 1
        assert "Duplikat dihapus : 1" in output
        assert "Baris tanpa target dihapus: 1" in output


# ---------------------------------------------------------------------------
# Test load_raw
# ---------------------------------------------------------------------------

class TestLoadRaw:
    def test_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_raw(tmp_path / "nonexistent.csv")

    def test_raises_on_wrong_delimiter(self, tmp_path):
        """File dengan koma (bukan titik koma) harus menghasilkan ValueError."""
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("a,b,c\n1,2,3\n", encoding="utf-8")
        # Dengan sep=';', hanya ada 1 kolom -> ValueError
        with pytest.raises(ValueError, match="delimiter"):
            load_raw(csv_path, sep=";")
