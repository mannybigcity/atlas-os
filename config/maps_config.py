from pathlib import Path
import os
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"

load_dotenv(env_path)

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")