-- Tabel: bank_campaign | Interpretasi ditulis di notebooks/04 berdasarkan output aktual.

-- Q0. Validasi jumlah baris (bandingkan dengan jumlah baris data sumber)
SELECT COUNT(*) AS total_rows FROM bank_campaign;

-- Q1. KPI kampanye
SELECT COUNT(*)                          AS total_kontak,
       COUNT(*) FILTER (WHERE y = 'yes') AS jumlah_yes,
       COUNT(*) FILTER (WHERE y = 'no')  AS jumlah_no,
       ROUND(100.0 * COUNT(*) FILTER (WHERE y = 'yes') / COUNT(*), 2) AS response_rate_pct
FROM bank_campaign;

-- Q2. Response rate per pekerjaan (sertakan ukuran sampel)
SELECT job, COUNT(*) AS total_kontak,
       COUNT(*) FILTER (WHERE y = 'yes') AS jumlah_yes,
       ROUND(100.0 * COUNT(*) FILTER (WHERE y = 'yes') / COUNT(*), 2) AS response_rate_pct
FROM bank_campaign GROUP BY job ORDER BY response_rate_pct DESC, total_kontak DESC;

-- Q3. Response rate per pendidikan
SELECT education, COUNT(*) AS total_kontak,
       COUNT(*) FILTER (WHERE y = 'yes') AS jumlah_yes,
       ROUND(100.0 * COUNT(*) FILTER (WHERE y = 'yes') / COUNT(*), 2) AS response_rate_pct
FROM bank_campaign GROUP BY education ORDER BY response_rate_pct DESC;

-- Q4. Response rate per kelompok usia
SELECT CASE WHEN age < 25 THEN '<25'
            WHEN age < 35 THEN '25-34'
            WHEN age < 45 THEN '35-44'
            WHEN age < 55 THEN '45-54'
            WHEN age < 65 THEN '55-64'
            ELSE '65+' END AS kelompok_usia,
       COUNT(*) AS total_kontak,
       ROUND(100.0 * COUNT(*) FILTER (WHERE y = 'yes') / COUNT(*), 2) AS response_rate_pct
FROM bank_campaign GROUP BY 1 ORDER BY MIN(age);

-- Q5. Response rate per jenis kontak
SELECT contact, COUNT(*) AS total_kontak,
       ROUND(100.0 * COUNT(*) FILTER (WHERE y = 'yes') / COUNT(*), 2) AS response_rate_pct
FROM bank_campaign GROUP BY contact ORDER BY response_rate_pct DESC;

-- Q6. Hubungan jumlah kontak kampanye dengan response rate
SELECT campaign AS jumlah_kontak, COUNT(*) AS total_kontak,
       ROUND(100.0 * COUNT(*) FILTER (WHERE y = 'yes') / COUNT(*), 2) AS response_rate_pct
FROM bank_campaign GROUP BY campaign ORDER BY campaign;

-- Q7. Response rate berdasarkan hasil kampanye sebelumnya
SELECT poutcome, COUNT(*) AS total_kontak,
       ROUND(100.0 * COUNT(*) FILTER (WHERE y = 'yes') / COUNT(*), 2) AS response_rate_pct
FROM bank_campaign GROUP BY poutcome ORDER BY response_rate_pct DESC;

-- Q8. Response rate per bulan
SELECT month, COUNT(*) AS total_kontak,
       ROUND(100.0 * COUNT(*) FILTER (WHERE y = 'yes') / COUNT(*), 2) AS response_rate_pct
FROM bank_campaign GROUP BY month ORDER BY total_kontak DESC;
