-- schema.sql
-- Skema utama untuk database bank_campaign_db.
-- Jalankan di database bank_campaign_db:
--   CREATE DATABASE bank_campaign_db;
--   psql -d bank_campaign_db -f sql/schema.sql

CREATE TABLE IF NOT EXISTS bank_campaign (
    id         BIGSERIAL PRIMARY KEY,
    age        SMALLINT     NOT NULL CHECK (age BETWEEN 18 AND 120),
    job        VARCHAR(30)  NOT NULL,
    marital    VARCHAR(20)  NOT NULL,
    education  VARCHAR(20)  NOT NULL,
    "default"  VARCHAR(3)   NOT NULL CHECK ("default" IN ('yes','no','unknown')),
    balance    INTEGER      NOT NULL,
    housing    VARCHAR(3)   NOT NULL CHECK (housing IN ('yes','no','unknown')),
    loan       VARCHAR(3)   NOT NULL CHECK (loan IN ('yes','no','unknown')),
    contact    VARCHAR(20)  NOT NULL,
    day        SMALLINT     NOT NULL CHECK (day BETWEEN 1 AND 31),
    month      VARCHAR(3)   NOT NULL,
    duration   INTEGER      NOT NULL CHECK (duration >= 0),  -- hanya analisis deskriptif
    campaign   SMALLINT     NOT NULL CHECK (campaign >= 1),
    pdays      INTEGER      NOT NULL,                         -- -1 = belum pernah dikontak
    previous   SMALLINT     NOT NULL CHECK (previous >= 0),
    poutcome   VARCHAR(20)  NOT NULL,
    y          VARCHAR(3)   NOT NULL CHECK (y IN ('yes','no'))
);

-- Indeks untuk mempercepat query segmentasi dan filter target
CREATE INDEX IF NOT EXISTS idx_bank_campaign_y          ON bank_campaign (y);
CREATE INDEX IF NOT EXISTS idx_bank_campaign_job        ON bank_campaign (job);
CREATE INDEX IF NOT EXISTS idx_bank_campaign_education  ON bank_campaign (education);
CREATE INDEX IF NOT EXISTS idx_bank_campaign_month      ON bank_campaign (month);
CREATE INDEX IF NOT EXISTS idx_bank_campaign_poutcome   ON bank_campaign (poutcome);
