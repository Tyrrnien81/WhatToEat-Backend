-- Align existing DBs with app.models.tracking.UserPreference
-- Run once in Supabase SQL Editor (or via sync_schema_and_seed_dev_user.py)

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'user_preferences'
      AND column_name = 'favorite_dining_halls'
  ) THEN
    ALTER TABLE user_preferences ADD COLUMN favorite_dining_halls JSONB DEFAULT '[]'::jsonb;
  END IF;
END $$;
