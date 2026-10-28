"""
predict.py
Fungsi prediksi terstandar untuk model tersimpan (best_model.joblib).

Penggunaan:
    from src.predict import predict_one

    hasil = predict_one({
        'age': 35, 'job': 'technician', 'marital': 'married',
        'education': 'secondary', 'default': 'no', 'balance': 1000,
        'housing': 'yes', 'loan': 'no', 'contact': 'cellular',
        'day': 15, 'month': 'may', 'campaign': 2, 'pdays': -1,
        'previous': 0, 'poutcome': 'unknown'
    })
    print(hasil)
"""

from pathlib import Path
import joblib
import pandas as pd

from src.feature_engineering import ALL_FEATURE_COLUMNS, NUMERIC_FEATURES

# Path default model; bisa di-override saat pemanggilan
_DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "best_model.joblib"


def predict_one(
    record: dict,
    model_path: str | Path | None = None,
) -> dict:
    """Prediksi satu calon nasabah menggunakan pipeline tersimpan.

    Args:
        record: Dict berisi nilai fitur (tanpa kolom 'duration' dan 'y').
                Kolom yang diperlukan: ALL_FEATURE_COLUMNS (15 kolom).
        model_path: Lokasi file .joblib. Default: models/best_model.joblib.

    Returns:
        Dict dengan kunci:
            - 'prediction'      : 'yes' atau 'no'
            - 'probability_yes' : float probabilitas kelas 'yes'
            - 'note'            : peringatan interpretasi

    Raises:
        FileNotFoundError: Jika file model tidak ditemukan.
        ValueError:        Jika input tidak lengkap atau tipe numerik salah.
    """
    model_path = Path(model_path or _DEFAULT_MODEL_PATH)
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model tidak ditemukan di {model_path}. "
            "Jalankan notebook 03 terlebih dahulu untuk melatih dan menyimpan model."
        )

    # Validasi kelengkapan kolom
    missing = [col for col in ALL_FEATURE_COLUMNS if col not in record]
    if missing:
        raise ValueError(f"Input tidak lengkap. Kolom hilang: {missing}")

    # Susun DataFrame satu baris
    row = pd.DataFrame([{col: record[col] for col in ALL_FEATURE_COLUMNS}])

    # Konversi fitur numerik
    for col in NUMERIC_FEATURES:
        try:
            row[col] = pd.to_numeric(row[col])
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Input tidak valid: kolom '{col}' harus bertipe angka."
            ) from exc

    model = joblib.load(model_path)
    proba = float(model.predict_proba(row)[0, 1])
    label = "yes" if int(model.predict(row)[0]) == 1 else "no"

    return {
        "prediction": label,
        "probability_yes": round(proba, 4),
        "note": (
            "Probabilitas adalah perkiraan model berdasarkan data historis kampanye "
            "di Portugal, bukan jaminan nasabah akan berlangganan. "
            "Gunakan sebagai panduan prioritisasi, bukan keputusan final."
        ),
    }


def predict_batch(
    df: "pd.DataFrame",
    model_path: str | Path | None = None,
) -> "pd.DataFrame":
    """Prediksi sekumpulan data baru (DataFrame).

    Args:
        df: DataFrame dengan kolom ALL_FEATURE_COLUMNS.
        model_path: Lokasi file .joblib.

    Returns:
        DataFrame asli ditambah kolom 'prediction' dan 'probability_yes'.
    """
    model_path = Path(model_path or _DEFAULT_MODEL_PATH)
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model tidak ditemukan di {model_path}. Jalankan notebook 03 terlebih dahulu."
        )
    missing = [col for col in ALL_FEATURE_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Kolom hilang: {missing}")

    X = df[ALL_FEATURE_COLUMNS].copy()
    for col in NUMERIC_FEATURES:
        try:
            X[col] = pd.to_numeric(X[col], errors="raise")
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Input tidak valid: kolom '{col}' harus bertipe angka."
            ) from exc

    model = joblib.load(model_path)
    probas = model.predict_proba(X)[:, 1]
    preds = model.predict(X)

    result = df.copy()
    result["probability_yes"] = probas.round(4)
    result["prediction"] = ["yes" if p == 1 else "no" for p in preds]
    return result
