from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext
from .db import get_connection
from .config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ===== Helpers =====
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ hoặc đã hết hạn")

@router.post("/register")
def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    conn = get_connection()
    cur = conn.cursor()

    # ✅ Kiểm tra user trùng
    cur.execute("SELECT 1 FROM Users WHERE username=? OR email=?", (username, email))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Tên đăng nhập hoặc email đã tồn tại.")

    # ✅ Hash mật khẩu
    hashed_pw = hash_password(password)

    # ✅ Tạo user mới (user thường mặc định)
    cur.execute("""
        INSERT INTO Users (username, email, password_hash, is_active, is_admin)
        VALUES (?, ?, ?, 1, 0)
    """, (username, email, hashed_pw))
    conn.commit()

    return {"message": "✅ Đăng ký tài khoản thành công."}

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Users WHERE username=?", (username,))
    user = cur.fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu")

    # ✅ Kiểm tra trạng thái kích hoạt
    if user.get("is_active", 1) == 0:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị vô hiệu hóa.")

    # ✅ Kiểm tra mật khẩu
    if not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu")

    # ✅ Thêm is_admin vào payload của token
    token_data = {
        "sub": user["username"],
        "user_id": user["user_id"],
        "is_admin": user.get("is_admin", 0)
    }

    token = create_access_token(token_data)
    return {"access_token": token, "token_type": "bearer"}
