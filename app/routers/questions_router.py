from fastapi import APIRouter, Depends, HTTPException, Form, Path
from ..db import get_connection
from .auth_router import get_current_user
from datetime import date  # <-- THÊM MỚI: Để xử lý lọc theo ngày

router = APIRouter(prefix="/questions", tags=["Questions"])

# =========================================================================
# === HÀM GET /QUESTIONS ĐÃ ĐƯỢC NÂNG CẤP TOÀN DIỆN ===
# =========================================================================

@router.get("/")
async def get_questions_advanced(
    # --- Xác thực ---
    user=Depends(get_current_user),
    
    # --- Tham số Tìm kiếm ---
    search_term: str | None = None,
    search_in_question: bool = True, 
    search_in_options: bool = False, 
    
    # --- Tham số Lọc ---
    file_id: int | None = None,
    status: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    
    # --- Tham số Sắp xếp ---
    sort_by: str | None = "newest"
):
    """
    Nâng cấp: Lấy câu hỏi với hệ thống lọc, tìm kiếm, sắp xếp động.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        user_id = user["user_id"]
        
        # === 1. XÂY DỰNG CÂU LỆNH SQL ĐỘNG ===
        sql_query = """
            SELECT q.*, e.total_score, e.accuracy_score, e.alignment_score,
                   e.distractors_score, e.clarity_score, e.status_by_agent
            FROM Questions q
            LEFT JOIN QuestionEvaluations e ON q.latest_evaluation_id = e.evaluation_id
        """
        where_clauses = ["q.creator_id = %s"]
        params = [user_id]
        
        # --- 2. THÊM LỌC (FILTER) ---
        if file_id:
            where_clauses.append("q.source_file_id = %s")
            params.append(file_id)
        if status:
            where_clauses.append("e.status_by_agent = %s") # Lọc theo status của AI
            params.append(status)
        if start_date:
            where_clauses.append("DATE(q.created_at) >= %s")
            params.append(start_date)
        if end_date:
            where_clauses.append("DATE(q.created_at) <= %s")
            params.append(end_date)

        # --- 3. THÊM TÌM KIẾM (SEARCH) ---
        if search_term:
            search_pattern = f"%{search_term}%"
            search_clauses = []
            
            if search_in_question:
                search_clauses.append("q.question_text LIKE %s")
                params.append(search_pattern)
            if search_in_options:
                search_clauses.append("q.options LIKE %s")
                params.append(search_pattern)
            
            if search_clauses:
                where_clauses.append(f"({' OR '.join(search_clauses)})")

        # --- 4. THÊM SẮP XẾP (SORT) ---
        order_clause = " ORDER BY "
        if sort_by == "score_high":
            order_clause += "e.total_score DESC, q.created_at DESC"
        elif sort_by == "score_low":
            order_clause += "e.total_score ASC, q.created_at DESC"
        elif sort_by == "oldest":
            order_clause += "q.created_at ASC"
        else: # Mặc định (newest)
            order_clause += "q.created_at DESC"

        # --- 5. TỔNG HỢP VÀ THỰC THI ---
        if where_clauses:
            sql_query += " WHERE " + " AND ".join(where_clauses)
        sql_query += order_clause
        
        cur.execute(sql_query, tuple(params))
        data = cur.fetchall()
        
        return {"count": len(data), "questions": data}
        
    except Exception as e:
        print(f"Lỗi khi get_questions_advanced: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ: {e}")
    finally:
        cur.close()
        conn.close()


# =========================================================================
# === CÁC HÀM KHÁC GIỮ NGUYÊN ===
# =========================================================================

@router.get("/{question_id}")
async def get_question_detail(question_id: int = Path(...), user=Depends(get_current_user)):
    """Get a single question (with evaluation)."""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT q.*, e.model_version, e.total_score, e.accuracy_score, e.alignment_score,
                   e.distractors_score, e.clarity_score, e.status_by_agent, e.raw_response_json
            FROM Questions q
            LEFT JOIN QuestionEvaluations e ON q.latest_evaluation_id = e.evaluation_id
            WHERE q.question_id = %s AND q.creator_id = %s
        """, (question_id, user["user_id"]))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Question not found.")
        return row
    finally:
        cur.close(); conn.close()

@router.put("/{question_id}")
async def update_question(
    question_id: int = Path(...),
    question_text: str = Form(...),
    options_json: str = Form(...),
    answer_letter: str = Form(...),
    status: str = Form("TEMP"),
    user=Depends(get_current_user)
):
    """Update question content."""
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE Questions
            SET question_text = %s, options = %s, answer_letter = %s, status = %s, updated_at = NOW()
            WHERE question_id = %s AND creator_id = %s
        """, (question_text, options_json, answer_letter, status, question_id, user["user_id"]))
        conn.commit()
        if cur.rowcount == 0:
            cur.execute("SELECT question_id FROM Questions WHERE question_id=%s AND creator_id=%s",
                        (question_id, user["user_id"]))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Question not found.")
        return {"message": "✅ Question updated successfully."}
    finally:
        cur.close(); conn.close()

@router.delete("/{question_id}")
async def delete_question(question_id: int, user=Depends(get_current_user)):
    """Delete question and its evaluations."""
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM QuestionEvaluations WHERE question_id=%s", (question_id,))
        cur.execute("""
            DELETE FROM Questions
            WHERE question_id=%s AND creator_id=%s
        """, (question_id, user["user_id"]))
        affected_rows = cur.rowcount
        conn.commit()

        if affected_rows == 0:
            cur.execute("SELECT question_id FROM Questions WHERE question_id=%s AND creator_id=%s",
                        (question_id, user["user_id"]))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Question not found.")
        return {"message": "🗑️ Question and evaluations deleted."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Delete error: {e}")
    finally:
        cur.close(); conn.close()