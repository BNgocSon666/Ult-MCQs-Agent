import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env (if present)
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Google API key (optional)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Max upload file size in MB (default: 20)
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB"))

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES"))


# === CẤU HÌNH LTI 1.3 ===
# URL CỦA BẠN (ví dụ: https://api.my-app.com)
APP_BASE_URL = "https://ultimate-mcqs-agent.onrender.com"
REACT_BASE_URL = "https://bnson.id.vn" 

# CẤU HÌNH Moodle/Canvas (LMS sẽ cung cấp)
LTI_CLIENT_ID = "s07BrmNCveYySoV"
LTI_DEPLOYMENT_ID = "1"
LTI_AUTH_LOGIN_URL = "https://ultimatemcqsagent.moodlecloud.com/mod/lti/auth.php"
LTI_AUTH_TOKEN_URL = "https://ultimatemcqsagent.moodlecloud.com/mod/lti/token.php"
LTI_KEY_SET_URL = "https://ultimatemcqsagent.moodlecloud.com/mod/lti/certs.php"

# CẶP KHÓA CỦA BẠN (Bạn tự tạo)
# Tạo bằng: openssl genrsa -out private.key 2048
#           openssl rsa -in private.key -pubout -out public.key
LTI_PRIVATE_KEY_FILE = BASE_DIR / "private.key"
LTI_PUBLIC_KEY_FILE = BASE_DIR / "public.key"
