from supabase import create_client

SUPABASE_URL = "https://sckvjvcywdlthsztsuau.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNja3ZqdmN5d2RsdGhzenRzdWF1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDMyMzY3OCwiZXhwIjoyMDg5ODk5Njc4fQ.ZuMB6KNUMHOnF3oSg60tP8rCCDxoe6kior1Xxaefz0k"

USER_ID = "738c95fb-b7f5-492a-9ff8-101603bf965d"

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

result = supabase.auth.admin.update_user_by_id(
    USER_ID,
    {"email_confirm": True}
)

print(result)