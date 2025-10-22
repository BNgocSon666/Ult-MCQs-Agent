import os
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

# Google API key (optional)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Max upload file size in MB (default: 20)
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
