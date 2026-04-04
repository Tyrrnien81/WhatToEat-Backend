# Supabase Scheduler Agent Task Spec

## Objective
Automate menu ingestion from Nutrislice into Supabase Postgres on a fixed schedule, with idempotent upserts and run observability.

## Inputs
- Supabase project URL
- Supabase service role key
- Upstream base URL: https://wisc-housingdining.api.nutrislice.com/menu/api/weeks/school
- Restaurant slugs:
  - carsons-market
  - four-lakes-market
  - gordon-avenue-market
  - lizs-market
  - lowell-market
  - rhetas-market
- Meal slugs:
  - breakfast
  - lunch
  - dinner
- Skip rule:
  - carsons-market + breakfast

## Required SQL (run in order)
1. sql/init.sql
2. sql/2026-04-03_ingest_hardening.sql
3. sql/2026-04-03_ingest_run_rpcs.sql

## Supabase Dashboard Steps
1. Open project.
2. SQL Editor:
   - Run the 3 SQL files above.
3. Edge Functions:
   - Create function named ingest-menu.
4. Edge Function Secrets:
   - SUPABASE_URL
   - SUPABASE_SERVICE_ROLE_KEY
   - TARGET_MENU_API_BASE
5. Deploy function.
6. Test invoke once manually with JSON body:
   - {"requestedDate":"2026-04-03","triggerSource":"manual"}
7. Verify logs and ingest_runs row creation/update.
8. Schedules (Cron): create 3 schedules targeting ingest-menu.

## Cron Schedule (CDT -> UTC)
Target local run times (CDT):
- 05:30
- 11:30
- 17:30

UTC equivalents while CDT is active (UTC-5):
- 10:30 UTC -> cron: 30 10 * * *
- 16:30 UTC -> cron: 30 16 * * *
- 22:30 UTC -> cron: 30 22 * * *

Note:
- Supabase cron uses UTC.
- After DST ends (CST, UTC-6), update schedule or accept 1-hour local drift.

## Edge Function Behavior Requirements
1. Call begin_ingest_run at start.
2. Fetch weekly endpoint per market/meal/target date.
3. Flatten payload into existing schema model.
4. Upsert in this order:
   - restaurants
   - meal_types
   - foods
   - food_nutrition
   - food_icons
   - food_icon_assignments
   - menu_snapshots
   - menu_sections
   - menu_section_items
5. Respect unique constraints from hardening migration.
6. On success, call finish_ingest_run with:
   - status=success
   - counters populated
7. On partial failures, call finish_ingest_run with:
   - status=partial
   - error_count > 0
   - concise error_message
8. On fatal failure, call finish_ingest_run with:
   - status=failed
   - error_message set

## Acceptance Criteria
1. Manual run succeeds and writes rows without duplicates on repeated runs.
2. Scheduled runs execute 3 times daily.
3. ingest_runs captures each run with final status and counts.
4. Re-running same date does not duplicate menu_sections/menu_section_items.
5. Backend reads from Supabase DB successfully.

## Minimal RPC Usage Example
Start run:
- select public.begin_ingest_run('scheduled', '2026-04-03', 6, 17, '{"source":"edge-function"}'::jsonb);

Finish run success:
- select public.finish_ingest_run(
    123,
    'success',
    17,
    93,
    12000,
    0,
    null,
    '{"durationMs": 8421}'::jsonb
  );

Finish run failure:
- select public.finish_ingest_run(
    123,
    'failed',
    17,
    0,
    0,
    1,
    'Upstream timeout for four-lakes-market/lunch',
    '{"failedPair":"four-lakes-market/lunch"}'::jsonb
  );
