from fastapi import APIRouter, Form, HTTPException, Depends
from jose import jwt, JWTError
from passlib.context import CryptContext
from ..db import get_connection
from ..config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login", 
    auto_error=False # <-- Không báo lỗi nếu không có token
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        username = payload.get("sub")
        is_admin = payload.get("is_admin", 0)
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT is_active FROM Users WHERE user_id=?", (user_id,))
        user = cur.fetchone()
        cur.close(); conn.close()

        if not user:
            raise HTTPException(status_code=401, detail="User not found.")
        if user["is_active"] == 0:
            raise HTTPException(status_code=403, detail="Account disabled.")

        return {"username": username, "user_id": user_id, "is_admin": is_admin}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def get_optional_current_user(token: Optional[str] = Depends(optional_oauth2_scheme)):
    """
    Cố gắng xác thực người dùng.
    Trả về `user` dict nếu token hợp lệ.
    Trả về `None` nếu không có token hoặc token không hợp lệ.
    """
    if not token:
        # Không có token (người dùng là khách)
        return None
    
    try:
        # Có token, giải mã nó
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        username = payload.get("sub")

        if user_id is None:
            return None # Token hợp lệ nhưng không có user_id

        # Vẫn kiểm tra xem user có tồn tại và active không
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT is_active FROM Users WHERE user_id=?", (user_id,))
        user_db = cur.fetchone()
        cur.close(); conn.close()

        if not user_db or user_db["is_active"] == 0:
            return None # User không tồn tại hoặc đã bị vô hiệu hóa

        # Trả về thông tin user
        return {"username": username, "user_id": user_id, "is_admin": payload.get("is_admin", 0)}

    except JWTError:
        # Token không hợp lệ (hết hạn, sai chữ ký, v.v.)
        return None

@router.post("/register")
def register(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM Users WHERE username=? OR email=?", (username, email))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Username hoặc email đã tồn tại")
    hashed = hash_password(password)
    cur.execute("INSERT INTO Users (username, email, password_hash, is_active) VALUES (?, ?, ?, 1)",
                (username, email, hashed))
    conn.commit()
    return {"message": "Đăng ký thành công"}

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Users WHERE username=?", (username,))
    user = cur.fetchone()
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu")
    token = create_access_token({"sub": user["username"], "user_id": user["user_id"], "is_admin": user.get("is_admin", 0)})
    return {"access_token": token, "token_type": "bearer"}
