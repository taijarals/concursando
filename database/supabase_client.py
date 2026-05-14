from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Remove partes inválidas
url = (
    url
    .replace("/rest/v1", "")
    .rstrip("/")
)

supabase = create_client(url, key)