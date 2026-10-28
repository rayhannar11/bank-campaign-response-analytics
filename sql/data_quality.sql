-- data_quality.sql
-- Query validasi kualitas data setelah data dimuat ke PostgreSQL.
-- Jalankan setelah import data dari notebook 04.
-- Seluruh query idealnya mengembalikan nol baris atau nilai 0 sebagai tanda data sudah bersih.

-- ============================================================
-- DQ-01. Jumlah total baris (bandingkan dengan 45.211 dari CSV)
-- ============================================================
SELECT COUNT(*) AS total_rows FROM bank_campaign;

-- ============================================================
-- DQ-02. Cek missing values per kolom
-- Semua kolom NOT NULL, sehingga hasil yang valid adalah 0.
-- ============================================================
SELECT
    COUNT(*) FILTER (WHERE age IS NULL)       AS null_age,
    COUNT(*) FILTER (WHERE job IS NULL)       AS null_job,
    COUNT(*) FILTER (WHERE marital IS NULL)   AS null_marital,
    COUNT(*) FILTER (WHERE education IS NULL) AS null_education,
    COUNT(*) FILTER (WHERE "default" IS NULL) AS null_default,
    COUNT(*) FILTER (WHERE balance IS NULL)   AS null_balance,
    COUNT(*) FILTER (WHERE housing IS NULL)   AS null_housing,
    COUNT(*) FILTER (WHERE loan IS NULL)      AS null_loan,
    COUNT(*) FILTER (WHERE contact IS NULL)   AS null_contact,
    COUNT(*) FILTER (WHERE day IS NULL)       AS null_day,
    COUNT(*) FILTER (WHERE month IS NULL)     AS null_month,
    COUNT(*) FILTER (WHERE duration IS NULL)  AS null_duration,
    COUNT(*) FILTER (WHERE campaign IS NULL)  AS null_campaign,
    COUNT(*) FILTER (WHERE pdays IS NULL)     AS null_pdays,
    COUNT(*) FILTER (WHERE previous IS NULL)  AS null_previous,
    COUNT(*) FILTER (WHERE poutcome IS NULL)  AS null_poutcome,
    COUNT(*) FILTER (WHERE y IS NULL)         AS null_y
FROM bank_campaign;

-- ============================================================
-- DQ-03. Cek duplikat baris (tanpa kolom id)
-- Hasil valid: 0 baris duplikat.
-- ============================================================
SELECT
    age, job, marital, education, "default", balance, housing, loan,
    contact, day, month, duration, campaign, pdays, previous, poutcome, y,
    COUNT(*) AS jumlah
FROM bank_campaign
GROUP BY
    age, job, marital, education, "default", balance, housing, loan,
    contact, day, month, duration, campaign, pdays, previous, poutcome, y
HAVING COUNT(*) > 1
ORDER BY jumlah DESC;

-- ============================================================
-- DQ-04. Validasi nilai target (hanya 'yes'/'no')
-- Baris dengan nilai lain harus kosong.
-- ============================================================
SELECT y, COUNT(*) AS jumlah
FROM bank_campaign
WHERE y NOT IN ('yes', 'no')
GROUP BY y;

-- ============================================================
-- DQ-05. Validasi rentang usia (18–120 sesuai constraint schema)
-- ============================================================
SELECT
    MIN(age) AS usia_minimum,
    MAX(age) AS usia_maksimum,
    COUNT(*) FILTER (WHERE age < 18 OR age > 120) AS usia_tidak_valid
FROM bank_campaign;

-- ============================================================
-- DQ-06. Distribusi nilai pdays
-- -1 = belum pernah dihubungi; nilai positif = jumlah hari sejak kontak terakhir.
-- ============================================================
SELECT
    CASE WHEN pdays = -1 THEN 'belum_pernah_dikontak'
         WHEN pdays BETWEEN 0 AND 30 THEN '0-30 hari'
         WHEN pdays BETWEEN 31 AND 90 THEN '31-90 hari'
         ELSE '>90 hari'
    END AS kelompok_pdays,
    COUNT(*) AS jumlah
FROM bank_campaign
GROUP BY 1
ORDER BY MIN(pdays);

-- ============================================================
-- DQ-07. Jumlah dan proporsi nilai 'unknown' per kolom kategorikal
-- ============================================================
SELECT 'job'       AS kolom, COUNT(*) AS jumlah_unknown FROM bank_campaign WHERE job = 'unknown'
UNION ALL
SELECT 'education',           COUNT(*) FROM bank_campaign WHERE education = 'unknown'
UNION ALL
SELECT 'contact',             COUNT(*) FROM bank_campaign WHERE contact = 'unknown'
UNION ALL
SELECT 'poutcome',            COUNT(*) FROM bank_campaign WHERE poutcome = 'unknown'
ORDER BY jumlah_unknown DESC;

-- ============================================================
-- DQ-08. Validasi jumlah campaign (harus >= 1)
-- ============================================================
SELECT
    MIN(campaign) AS campaign_min,
    MAX(campaign) AS campaign_max,
    COUNT(*) FILTER (WHERE campaign < 1) AS campaign_tidak_valid
FROM bank_campaign;

-- ============================================================
-- DQ-09. Validasi saldo (balance) – tidak ada constraint range,
--         tetapi nilai negatif ekstrem perlu diperhatikan
-- ============================================================
SELECT
    MIN(balance)  AS balance_minimum,
    MAX(balance)  AS balance_maksimum,
    AVG(balance)  AS balance_rata_rata,
    COUNT(*) FILTER (WHERE balance < -10000) AS balance_ekstrem_negatif
FROM bank_campaign;

-- ============================================================
-- DQ-10. Baris dengan nilai month di luar nama 12 bulan harus kosong.
-- ============================================================
SELECT month, COUNT(*) AS jumlah
FROM bank_campaign
WHERE month NOT IN (
    'jan', 'feb', 'mar', 'apr', 'may', 'jun',
    'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
)
GROUP BY month
ORDER BY month;
