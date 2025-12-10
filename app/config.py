import os
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

# Google API key (optional)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Max upload file size in MB (default: 20)
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB"))

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES"))

LTI_PRIVATE_KEY_FILE = os.getenv("LTI_PRIVATE_KEY_FILE")
LTI_PUBLIC_KEY_FILE = os.getenv("LTI_PUBLIC_KEY_FILE")
LTI_ISSUER_ID = os.getenv("LTI_ISSUER_ID")
LTI_CLIENT_ID = os.getenv("LTI_CLIENT_ID")
LTI_DEPLOYMENT_ID = os.getenv("LTI_DEPLOYMENT_ID")
LTI_AUTH_LOGIN_URL = os.getenv("LTI_AUTH_LOGIN_URL")
LTI_AUTH_TOKEN_URL = os.getenv("LTI_AUTH_TOKEN_URL")
LTI_KEY_SET_URL = os.getenv("LTI_KEY_SET_URL")

REACT_BASE_URL = os.getenv("REACT_BASE_URL")
APP_BASE_URL = os.getenv("APP_BASE_URL")