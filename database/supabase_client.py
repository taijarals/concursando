from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("SUPABASE_URL").replace("/rest/v1/","").rstrip("/")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)