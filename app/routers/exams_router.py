from fastapi import APIRouter, Form, Depends, HTTPException
from ..db import get_connection
from .auth_router import get_current_user
import secrets

router = APIRouter(prefix="/exams", tags=["Exams"])

@router.post("/")
async def create_exam(
    title: str = Form(...),
    description: str = Form(""),
    question_ids: str = Form(...),
    user=Depends(get_current_user)
):
    # ... (code của bạn, đã dùng %s - ĐÚNG) ...
    conn = get_connection(); cur = conn.cursor()
    try:
        ids = [int(x.strip()) for x in question_ids.split(",") if x.strip().isdigit()]
        share_token = secrets.token_hex(8)  # generate 16-char unique token

        cur.execute("SELECT 1 FROM Exams WHERE share_token=%s", (share_token,))
        while cur.fetchone():
            share_token = secrets.token_hex(8)

        cur.execute("""
            INSERT INTO Exams (title, description, owner_id, share_token, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, (title, description, user["user_id"], share_token))
        exam_id = cur.lastrowid

        # link questions
        for qid in ids:
            cur.execute("INSERT INTO ExamQuestions (exam_id, question_id) VALUES (%s, %s)", (exam_id, qid))

        conn.commit()
        return {
            "exam_id": exam_id,
            "share_token": share_token,
            "message": f"✅ Exam created successfully with {len(ids)} questions."
        }
    except Exception as e:
        conn.rollback()
        print(f"LỖI NGHIÊM TRỌNG TẠI [tên_router]: {e}") 
        raise HTTPException(status_code=500, detail="Đã xảy ra lỗi máy chủ nội bộ.")
    finally:
        cur.close(); conn.close()

@router.get("/")
async def get_exams(user=Depends(get_current_user)):
    # ... (code của bạn, đã dùng %s - ĐÚNG) ...
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT exam_id, title, description, created_at
            FROM Exams
            WHERE owner_id=%s
            ORDER BY created_at DESC
        """, (user["user_id"],))
        return {"exams": cur.fetchall()}
    finally:
        cur.close(); conn.close()

@router.get("/{exam_id}")
async def get_exam_detail(exam_id: int, user=Depends(get_current_user)):
    # ... (code của bạn, đã dùng %s - ĐÚNG) ...
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM Exams WHERE exam_id=%s AND owner_id=%s", (exam_id, user["user_id"]))
        exam = cur.fetchone()
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found.")
        cur.execute("""
            SELECT q.question_id, q.question_text, q.options, q.answer_letter
            FROM ExamQuestions eq
            JOIN Questions q ON eq.question_id = q.question_id
            WHERE eq.exam_id = %s
        """, (exam_id,))
        exam["questions"] = cur.fetchall()
        return exam
    finally:
        cur.close(); conn.close()

@router.delete("/{exam_id}")
async def delete_exam(exam_id: int, user=Depends(get_current_user)):
    # ... (code của bạn, đã dùng %s - ĐÚNG) ...
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Exams WHERE exam_id=%s AND owner_id=%s", (exam_id, user["user_id"]))
        affected = cur.rowcount
        conn.commit()
        if affected == 0:
            raise HTTPException(status_code=404, detail="Exam not found.")
        return {"message": "🗑️ Exam deleted successfully."}
    finally:
        cur.close(); conn.close()

@router.get("/token/{share_token}")
async def get_exam_by_token(share_token: str):
    """
    Lấy thông tin cơ bản của đề thi (title, description, exam_id)
    dùng cho trang làm bài công khai (public).
    Endpoint này KHÔNG cần xác thực.
    """
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT exam_id, title, description FROM Exams WHERE share_token = %s",
            (share_token,) # <-- ĐÃ SỬA TỪ ? THÀNH %s
        )
        exam = cur.fetchone()
        if not exam:
            raise HTTPException(status_code=404, detail="Không tìm thấy đề thi.")
        return exam
    finally:
        cur.close(); conn.close()

@router.get("/{exam_id}/results")
async def get_exam_results_by_owner(
    exam_id: int, 
    user=Depends(get_current_user)
):
    """
    [Dành cho chủ sở hữu] Lấy tất cả kết quả (sessions) 
    của một đề thi cụ thể.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        user_id = user["user_id"]
        
        # Câu lệnh SQL này làm 3 việc:
        # 1. JOIN ExamSessions (kết quả) với Exams (đề thi).
        # 2. Lọc theo exam_id VÀ owner_id (để đảm bảo bạn sở hữu đề này).
        # 3. Chỉ lấy các bài đã nộp (end_time IS NOT NULL).
        # 4. Dùng COALESCE để lấy username (nếu là user) hoặc guest_name (nếu là khách).
        
        sql_query = """
            SELECT 
                s.session_id, 
                s.total_score, 
                s.start_time,  -- <-- DÒNG MỚI ĐÃ THÊM
                s.end_time, 
                COALESCE(u.full_name, u.username, s.guest_name) AS taker_name,
                (SELECT COUNT(1) FROM ExamQuestions eq WHERE eq.exam_id = e.exam_id) AS total_questions
            FROM ExamSessions s
            JOIN Exams e ON s.exam_id = e.exam_id
            LEFT JOIN Users u ON s.user_id = u.user_id
            WHERE e.exam_id = %s AND e.owner_id = %s
            AND s.end_time IS NOT NULL
            ORDER BY s.end_time DESC;
        """
        
        cur.execute(sql_query, (exam_id, user_id))
        results = cur.fetchall()
        
        return {"results": results}
        
    except Exception as e:
        # In lỗi ra server log để debug
        print(f"Lỗi khi lấy kết quả exam: {e}") 
        raise HTTPException(status_code=500, detail="Đã xảy ra lỗi máy chủ nội bộ.")
    finally:
        cur.close()
        conn.close()