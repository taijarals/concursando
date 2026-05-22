"""Application settings and environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Sanitize Supabase URL
if SUPABASE_URL:
    SUPABASE_URL = SUPABASE_URL.replace("/rest/v1", "").rstrip("/")

# App
APP_NAME = "Concurso AI"
APP_ICON = "📚"
DEFAULT_THEME = "light"
LAYOUT = "wide"

# Database
DEFAULT_QUESTIONS_BATCH_SIZE = 20
MAX_PDF_UPLOAD_SIZE_MB = 50

# AI
DEFAULT_AI_MODEL = "gemini"
AI_TEMPERATURE = 0.7
AI_MAX_TOKENS = 2048

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "logs/app.log"
