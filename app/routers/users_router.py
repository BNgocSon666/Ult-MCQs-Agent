from fastapi import APIRouter, Depends, HTTPException, Form
from passlib.hash import bcrypt
from ..db import get_connection
from .auth_router import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

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
    username: str = Form(None),
    email: str = Form(None),
    password: str = Form(None),
    is_active: int = Form(1),
    user=Depends(get_current_user)
):
    """Update user info (self or admin only)."""
    conn = get_connection(); cur = conn.cursor()
    try:
        if user["user_id"] != user_id and user.get("is_admin", 0) == 0:
            raise HTTPException(status_code=403, detail="Permission denied.")

        password_hash = None
        if password:
            password_hash = bcrypt.hash(password)

        fields, params = [], []
        if username:
            fields.append("username=%s")
            params.append(username)
        if email:
            fields.append("email=%s")
            params.append(email)
        if password_hash:
            fields.append("password_hash=%s")
            params.append(password_hash)
        fields.append("is_active=%s")
        params.append(is_active)
        params.append(user_id)

        sql = f"UPDATE Users SET {', '.join(fields)} WHERE user_id=%s"
        cur.execute(sql, tuple(params))
        affected_rows = cur.rowcount
        conn.commit()

        if affected_rows == 0:
            cur.execute("SELECT user_id FROM Users WHERE user_id=%s", (user_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="User not found.")
        return {"message": "✅ User updated successfully."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Update error: {e}")
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
        raise HTTPException(status_code=500, detail=f"Deactivate error: {e}")
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
