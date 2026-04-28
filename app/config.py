"""Application configuration."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "app" / "data"

# Load .env from project root
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'finance.db'}")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DEBUG = os.getenv("DEBUG", "true").lower() in ("1", "true", "yes")
