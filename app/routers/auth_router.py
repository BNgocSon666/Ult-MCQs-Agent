from fastapi import APIRouter, Form, HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext
from ..db import get_connection
from ..config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from datetime import datetime, timedelta
from typing import Optional

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
