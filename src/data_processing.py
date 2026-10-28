"""Reusable data loading, validation, and cleaning functions."""

from pathlib import Path
import pandas as pd


EXPECTED_COLUMNS = [
    "age", "job", "marital", "education", "default", "balance", "housing", "loan",
    "contact", "day", "month", "duration", "campaign", "pdays", "previous", "poutcome", "y",
]
NUMERIC_COLUMNS = ["age", "balance", "day", "duration", "campaign", "pdays", "previous"]
CATEGORICAL_COLUMNS = [c for c in EXPECTED_COLUMNS if c not in NUMERIC_COLUMNS + ["y"]]
TARGET = "y"


def load_raw(path: str | Path, sep: str = ";") -> pd.DataFrame:
    """Baca file CSV mentah dan normalisasi nama kolom ke huruf kecil.

    Args:
        path: Lokasi file CSV.
        sep:  Delimiter (default ';' sesuai dataset UCI).

    Returns:
        DataFrame dengan kolom huruf kecil.

    Raises:
        FileNotFoundError: Jika file tidak ditemukan.
        ValueError:        Jika jumlah kolom tidak sesuai delimiter.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"{path.name} tidak ditemukan. Unduh dari UCI dan simpan di data/raw/."
        )
    df = pd.read_csv(path, sep=sep)
    if df.shape[1] == 1:
        raise ValueError(
            "Jumlah kolom tidak sesuai. Periksa delimiter (diharapkan ';')."
        )
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def validate_schema(df: pd.DataFrame, required: list[str] | None = None) -> None:
    """Validasi bahwa semua kolom wajib hadir.

    Raises:
        ValueError: Jika kolom wajib hilang atau ada kolom tak terduga.
    """
    required = required or EXPECTED_COLUMNS
    missing = sorted(set(required) - set(df.columns))
    extra = sorted(set(df.columns) - set(required))
    if missing or extra:
        raise ValueError(
            f"Skema kolom tidak sesuai. Hilang: {missing}; tambahan: {extra}"
        )


def validate_target(df: pd.DataFrame, target: str = TARGET) -> None:
    """Pastikan kolom target hanya berisi 'yes'/'no'.

    Raises:
        AssertionError: Jika kelas tidak lengkap atau terdapat nilai tak dikenal.
    """
    classes = set(df[target].dropna().unique())
    assert len(classes) == 2, "Target harus punya dua kelas"
    assert classes <= {"yes", "no"}, f"Nilai target tak terduga: {classes}"


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Pipeline pembersihan data lengkap.

    Langkah:
    1. Validasi skema kolom.
    2. Hapus baris duplikat identik.
    3. Normalkan kolom kategorikal (strip + lower).
    4. Konversi kolom numerik dengan `errors='raise'`.
    5. Hapus baris tanpa target; validasi nilai target.
    6. Isi missing kategorikal dengan 'unknown'.
    7. Biarkan missing numerik (akan diimputasi oleh pipeline ML).

    Returns:
        DataFrame bersih (copy baru).

    Raises:
        ValueError: Jika skema salah, nilai numerik tidak bisa dikonversi,
                    atau target mengandung nilai di luar {'yes', 'no'}.
    """
    validate_schema(df)
    df_clean = df[EXPECTED_COLUMNS].copy()

    # Normalisasi kategorikal
    for col in CATEGORICAL_COLUMNS + [TARGET]:
        df_clean[col] = (
            df_clean[col]
            .astype("string")
            .str.strip()
            .str.lower()
            .replace("", pd.NA)
        )

    # Konversi numerik (error jika ada nilai tidak bisa dikonversi)
    for col in NUMERIC_COLUMNS:
        df_clean[col] = pd.to_numeric(df_clean[col], errors="raise")

    # Hapus duplikat dan baris tanpa target; catat keduanya terpisah.
    rows_before = len(df_clean)
    duplicates_removed = int(df_clean.duplicated().sum())
    df_clean = df_clean.drop_duplicates().copy()
    rows_without_target_removed = int(df_clean[TARGET].isna().sum())
    df_clean = df_clean.dropna(subset=[TARGET]).copy()
    rows_after = len(df_clean)

    # Validasi target
    invalid_targets = sorted(set(df_clean[TARGET].dropna()) - {"yes", "no"})
    if invalid_targets:
        raise ValueError(f"Nilai target tidak dikenal: {invalid_targets}")

    # Isi missing kategorikal dengan 'unknown'
    for col in CATEGORICAL_COLUMNS:
        df_clean[col] = df_clean[col].fillna("unknown")

    # Ringkasan proses cleaning
    summary = {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "duplicates_removed": duplicates_removed,
        "rows_without_target_removed": rows_without_target_removed,
        "missing_remaining": int(df_clean.isna().sum().sum()),
        "pdays_not_contacted": int(df_clean["pdays"].eq(-1).sum()),
        "unknown_counts": {
            col: int(df_clean[col].eq("unknown").sum())
            for col in CATEGORICAL_COLUMNS
            if df_clean[col].eq("unknown").sum() > 0
        },
    }
    print(f"Baris: {summary['rows_before']:,} -> {summary['rows_after']:,}")
    print(f"Duplikat dihapus : {summary['duplicates_removed']:,}")
    print(f"Baris tanpa target dihapus: {summary['rows_without_target_removed']:,}")
    print(f"Missing tersisa  : {summary['missing_remaining']:,}")
    print(f"pdays = -1       : {summary['pdays_not_contacted']:,}")
    if summary["unknown_counts"]:
        print("Unknown per kolom:", summary["unknown_counts"])

    return df_clean


def save_clean(df: pd.DataFrame, path: str | Path) -> None:
    """Simpan DataFrame bersih ke CSV dan validasi hasil simpan.

    Raises:
        AssertionError: Jika jumlah baris atau kolom tidak konsisten.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

    check = pd.read_csv(path)
    assert len(check) == len(df), "Jumlah baris berbeda setelah disimpan."
    assert check.columns.tolist() == df.columns.tolist(), (
        "Nama kolom berbeda setelah disimpan."
    )
    print(f"Dataset tersimpan dan tervalidasi: {path.name}")
    print(f"Baris: {len(check):,} | Kolom: {len(check.columns)}")
