from fastapi import APIRouter, Depends, HTTPException, Form
from passlib.hash import bcrypt
from ..db import get_connection
from .auth_router import get_current_user, verify_password
from datetime import date

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
async def get_current_user_profile(user: dict = Depends(get_current_user)):
    """
    Trả về thông tin của user đang đăng nhập (đã được giải mã từ token).
    """
    # Hàm get_current_user (từ auth_router) đã làm hết mọi việc
    # (giải mã token, kiểm tra DB). Chúng ta chỉ cần trả về nó.
    return user

@router.get("/{user_id}")
async def get_user_detail(user_id: int, user=Depends(get_current_user)):
    """Get user info (self or admin only)."""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        if user["user_id"] != user_id and user.get("is_admin", 0) == 0:
            raise HTTPException(status_code=403, detail="Permission denied.")
        cur.execute("""
            SELECT user_id, username, email, is_active, created_at
            FROM Users
            WHERE user_id = %s
        """, (user_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found.")
        return row
    finally:
        cur.close(); conn.close()

@router.put("/{user_id}")
async def update_user(
    user_id: int,
    user=Depends(get_current_user),
    
    # --- Thông tin Profile ---
    username: str = Form(None),
    email: str = Form(None),
    full_name: str = Form(None),
    phone_number: str = Form(None),
    birth: date = Form(None),
    
    # --- Bảo mật ---
    old_password: str = Form(None),
    password: str = Form(None),     
    
    # --- Admin (Tùy chọn) ---
    is_active: int = Form(None) 
):
    """
    Update user info (self or admin only).
    Chỉ cập nhật các trường được cung cấp (kể cả chuỗi rỗng "").
    """
    
    # 1. Kiểm tra quyền (Giữ nguyên)
    is_admin = user.get("is_admin", 0)
    if user["user_id"] != user_id and is_admin == 0:
        raise HTTPException(status_code=403, detail="Permission denied.")

    fields, params = [], []

    # === 2. XỬ LÝ ĐỔI MẬT KHẨU (Giữ nguyên logic) ===
    if password: 
        if not old_password:
            raise HTTPException(status_code=400, detail="Vui lòng nhập mật khẩu cũ để đổi mật khẩu.")
        
        conn_pass = get_connection()
        cur_pass = conn_pass.cursor(dictionary=True)
        cur_pass.execute("SELECT password_hash FROM Users WHERE user_id=%s", (user_id,))
        user_db = cur_pass.fetchone()
        cur_pass.close(); conn_pass.close()

        if not user_db:
            raise HTTPException(status_code=404, detail="User not found.")
            
        if not verify_password(old_password, user_db["password_hash"]):
            raise HTTPException(status_code=403, detail="Mật khẩu cũ không chính xác.")
        
        password_hash = bcrypt.hash(password)
        fields.append("password_hash=%s")
        params.append(password_hash)

    # === 3. XỬ LÝ CÁC TRƯỜNG KHÁC (ĐÃ SỬA) ===
    # Chỉ cập nhật nếu field không phải None (tức là field CÓ được gửi lên)
    
    # Username và Email không nên cho phép rỗng
    if username is not None and username != "": 
        fields.append("username=%s")
        params.append(username)
    if email is not None and email != "": 
        fields.append("email=%s")
        params.append(email)
    
    # Cho phép full_name và phone_number là chuỗi rỗng "" (để xóa)
    if full_name is not None: 
        fields.append("full_name=%s")
        params.append(full_name)
    if phone_number is not None: 
        fields.append("phone_number=%s")
        params.append(phone_number)
        
    if birth: 
        fields.append("birth=%s")
        params.append(birth)
    
    if is_active is not None and is_admin == 1:
        fields.append("is_active=%s")
        params.append(is_active)
        
    # === 4. THỰC THI CẬP NHẬT (ĐÃ SỬA) ===
    if not fields:
        return {"message": "Không có thông tin nào được gửi để cập nhật."}

    params.append(user_id) 

    conn = get_connection(); cur = conn.cursor()
    try:
        sql = f"UPDATE Users SET {', '.join(fields)} WHERE user_id=%s"
        cur.execute(sql, tuple(params))
        # affected_rows = cur.rowcount # <-- BỎ KIỂM TRA NÀY
        conn.commit()

        # BỎ LỖI 404 NẾU KHÔNG CÓ GÌ THAY ĐỔI
        # if affected_rows == 0:
        #      raise HTTPException(status_code=404, detail="User not found or no data changed.")
        
        return {"message": "✅ User updated successfully."}
    except Exception as e:
        print(f"LỖI NGHIÊM TRỌNG TẠI [tên_router]: {e}")
        raise HTTPException(status_code=500, detail="Đã xảy ra lỗi máy chủ nội bộ.")
    finally:
        cur.close(); conn.close()

@router.put("/{user_id}/deactivate")
async def deactivate_user(user_id: int, user=Depends(get_current_user)):
    """Soft deactivate user."""
    conn = get_connection(); cur = conn.cursor()
    try:
        if user["user_id"] != user_id and user.get("is_admin", 0) == 0:
            raise HTTPException(status_code=403, detail="Permission denied.")
        cur.execute("UPDATE Users SET is_active=0 WHERE user_id=%s", (user_id,))
        affected_rows = cur.rowcount
        conn.commit()
        if affected_rows == 0:
            cur.execute("SELECT user_id FROM Users WHERE user_id=%s", (user_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="User not found.")
        return {"message": "🚫 User deactivated successfully."}
    except Exception as e:
        conn.rollback()
        print(f"LỖI NGHIÊM TRỌNG TẠI [tên_router]: {e}") 
        raise HTTPException(status_code=500, detail="Đã xảy ra lỗi máy chủ nội bộ.")
    finally:
        cur.close(); conn.close()

@router.put("/{user_id}/activate")
async def activate_user(user_id: int, user=Depends(get_current_user)):
    """Reactivate user (admin only)."""
    conn = get_connection(); cur = conn.cursor()
    try:
        if user.get("is_admin", 0) == 0:
            raise HTTPException(status_code=403, detail="Admin only.")
        cur.execute("UPDATE Users SET is_active=1 WHERE user_id=%s", (user_id,))
        conn.commit()
        return {"message": "✅ User reactivated successfully."}
    finally:
        cur.close(); conn.close()