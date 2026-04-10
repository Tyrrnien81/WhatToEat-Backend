import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

USER_ID = "738c95fb-b7f5-492a-9ff8-101603bf965d"

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

result = supabase.auth.admin.update_user_by_id(
    USER_ID,
    {"email_confirm": True}
)

print(result)