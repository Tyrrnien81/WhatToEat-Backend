-- Ingest hardening migration for Supabase/Postgres
-- Purpose:
-- 1) Prevent duplicate menu sections/items on repeated ingestion runs
-- 2) Add ingest_runs table for scheduler observability

BEGIN;

-- ============================================================
-- A. Deduplicate menu_sections by (snapshot_id, external_menu_id)
--    Keep the smallest id as canonical, re-point child rows,
--    then delete duplicate section rows.
-- ============================================================

WITH section_dupes AS (
  SELECT
    id,
    snapshot_id,
    external_menu_id,
    MIN(id) OVER (PARTITION BY snapshot_id, external_menu_id) AS keep_id
  FROM menu_sections
),
section_map AS (
  SELECT id AS old_id, keep_id
  FROM section_dupes
  WHERE id <> keep_id
)
UPDATE menu_section_items msi
SET section_id = sm.keep_id
FROM section_map sm
WHERE msi.section_id = sm.old_id;

WITH section_dupes AS (
  SELECT
    id,
    snapshot_id,
    external_menu_id,
    MIN(id) OVER (PARTITION BY snapshot_id, external_menu_id) AS keep_id
  FROM menu_sections
)
DELETE FROM menu_sections ms
USING section_dupes sd
WHERE ms.id = sd.id
  AND sd.id <> sd.keep_id;

-- ============================================================
-- B. Deduplicate menu_section_items for two identity cases:
--    1) external_menu_item_id exists  -> key: (section_id, external_menu_item_id)
--    2) external_menu_item_id is null -> fallback composite identity
-- ============================================================

-- Case 1: external_menu_item_id is present
WITH ranked AS (
  SELECT
    id,
    ROW_NUMBER() OVER (
      PARTITION BY section_id, external_menu_item_id
      ORDER BY id
    ) AS rn
  FROM menu_section_items
  WHERE external_menu_item_id IS NOT NULL
)
DELETE FROM menu_section_items msi
USING ranked r
WHERE msi.id = r.id
  AND r.rn > 1;

-- Case 2: external_menu_item_id is null (fallback identity)
WITH ranked AS (
  SELECT
    id,
    ROW_NUMBER() OVER (
      PARTITION BY
        section_id,
        COALESCE(food_id, -1),
        COALESCE(food_variation_id, -1),
        position,
        COALESCE(station_name, ''),
        COALESCE(category, ''),
        COALESCE(serving_size_amount, ''),
        COALESCE(serving_size_unit, ''),
        COALESCE(price, -1)
      ORDER BY id
    ) AS rn
  FROM menu_section_items
  WHERE external_menu_item_id IS NULL
)
DELETE FROM menu_section_items msi
USING ranked r
WHERE msi.id = r.id
  AND r.rn > 1;

COMMIT;

-- ============================================================
-- C. Add uniqueness guards for future ingests
-- ============================================================

-- menu_sections: one section per (snapshot, external_menu_id)
CREATE UNIQUE INDEX IF NOT EXISTS ux_menu_sections_snapshot_external_menu
  ON menu_sections (snapshot_id, external_menu_id);

-- menu_section_items case 1: when external_menu_item_id exists
CREATE UNIQUE INDEX IF NOT EXISTS ux_msi_section_external_item
  ON menu_section_items (section_id, external_menu_item_id)
  WHERE external_menu_item_id IS NOT NULL;

-- menu_section_items case 2: fallback uniqueness when external_menu_item_id is null
CREATE UNIQUE INDEX IF NOT EXISTS ux_msi_section_fallback_identity
  ON menu_section_items (
    section_id,
    COALESCE(food_id, -1),
    COALESCE(food_variation_id, -1),
    position,
    COALESCE(station_name, ''),
    COALESCE(category, ''),
    COALESCE(serving_size_amount, ''),
    COALESCE(serving_size_unit, ''),
    COALESCE(price, -1)
  )
  WHERE external_menu_item_id IS NULL;

-- ============================================================
-- D. Scheduler run observability table
-- ============================================================

CREATE TABLE IF NOT EXISTS ingest_runs (
  id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  trigger_source      TEXT NOT NULL,
  requested_date      DATE,
  started_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  finished_at         TIMESTAMPTZ,
  status              TEXT NOT NULL CHECK (status IN ('running', 'success', 'failed', 'partial')),
  markets_total       INT NOT NULL DEFAULT 0,
  meals_total         INT NOT NULL DEFAULT 0,
  requests_total      INT NOT NULL DEFAULT 0,
  files_or_days_total INT NOT NULL DEFAULT 0,
  rows_upserted_total INT NOT NULL DEFAULT 0,
  error_count         INT NOT NULL DEFAULT 0,
  error_message       TEXT,
  details             JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_ingest_runs_started_at_desc
  ON ingest_runs (started_at DESC);

CREATE INDEX IF NOT EXISTS ix_ingest_runs_status
  ON ingest_runs (status);

CREATE INDEX IF NOT EXISTS ix_ingest_runs_requested_date
  ON ingest_runs (requested_date);
