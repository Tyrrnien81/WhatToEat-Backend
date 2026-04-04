-- Ingest run RPC helpers for Supabase
-- Depends on: ingest_runs table from 2026-04-03_ingest_hardening.sql

BEGIN;

-- ============================================================
-- RPC 1: begin_ingest_run
-- Inserts a running row and returns ingest_runs.id
-- ============================================================

CREATE OR REPLACE FUNCTION public.begin_ingest_run(
  p_trigger_source TEXT,
  p_requested_date DATE DEFAULT NULL,
  p_markets_total INT DEFAULT 0,
  p_meals_total INT DEFAULT 0,
  p_details JSONB DEFAULT '{}'::jsonb
)
RETURNS BIGINT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_id BIGINT;
BEGIN
  INSERT INTO ingest_runs (
    trigger_source,
    requested_date,
    status,
    started_at,
    markets_total,
    meals_total,
    details
  )
  VALUES (
    p_trigger_source,
    p_requested_date,
    'running',
    NOW(),
    COALESCE(p_markets_total, 0),
    COALESCE(p_meals_total, 0),
    COALESCE(p_details, '{}'::jsonb)
  )
  RETURNING id INTO v_id;

  RETURN v_id;
END;
$$;

COMMENT ON FUNCTION public.begin_ingest_run(TEXT, DATE, INT, INT, JSONB)
IS 'Create a running ingest_runs row and return run id.';

-- ============================================================
-- RPC 2: finish_ingest_run
-- Updates counters/final status and sets finished_at
-- ============================================================

CREATE OR REPLACE FUNCTION public.finish_ingest_run(
  p_run_id BIGINT,
  p_status TEXT,
  p_requests_total INT DEFAULT NULL,
  p_files_or_days_total INT DEFAULT NULL,
  p_rows_upserted_total INT DEFAULT NULL,
  p_error_count INT DEFAULT NULL,
  p_error_message TEXT DEFAULT NULL,
  p_details JSONB DEFAULT NULL
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF p_status NOT IN ('success', 'failed', 'partial') THEN
    RAISE EXCEPTION 'Invalid p_status: %. Must be success, failed, or partial.', p_status;
  END IF;

  UPDATE ingest_runs
  SET
    status = p_status,
    finished_at = NOW(),
    requests_total = COALESCE(p_requests_total, requests_total),
    files_or_days_total = COALESCE(p_files_or_days_total, files_or_days_total),
    rows_upserted_total = COALESCE(p_rows_upserted_total, rows_upserted_total),
    error_count = COALESCE(p_error_count, error_count),
    error_message = COALESCE(p_error_message, error_message),
    details = COALESCE(p_details, details)
  WHERE id = p_run_id;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'ingest_runs row not found for id=%', p_run_id;
  END IF;
END;
$$;

COMMENT ON FUNCTION public.finish_ingest_run(BIGINT, TEXT, INT, INT, INT, INT, TEXT, JSONB)
IS 'Finalize ingest_runs row with status, counters, and error details.';

-- Optional explicit grants for RPC usage.
-- Service role bypasses RLS, but these grants make invocation explicit.
GRANT EXECUTE ON FUNCTION public.begin_ingest_run(TEXT, DATE, INT, INT, JSONB) TO service_role;
GRANT EXECUTE ON FUNCTION public.finish_ingest_run(BIGINT, TEXT, INT, INT, INT, INT, TEXT, JSONB) TO service_role;

COMMIT;
