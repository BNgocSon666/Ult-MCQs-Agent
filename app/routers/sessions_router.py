from fastapi import APIRouter, Depends, Form, HTTPException
from ..db import get_connection
from .agent_router import get_current_user
from ..schemas import SaveAnswersPayload

router = APIRouter(prefix="/exam_sessions", tags=["Exam Sessions"])

@router.post("/start")
async def start_exam(
    exam_id: int = Form(...),
    guest_name: str | None = Form(None),
    user=Depends(get_current_user)
):
    """Start exam session and return question list."""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        user_id = user["user_id"] if user else None
        cur.execute("""
            INSERT INTO ExamSessions (exam_id, user_id, guest_name, start_time)
            VALUES (%s, %s, %s, NOW())
        """, (exam_id, user_id, guest_name))
        session_id = cur.lastrowid

        cur.execute("""
            SELECT q.question_id, q.question_text, q.options
            FROM ExamQuestions eq
            JOIN Questions q ON eq.question_id = q.question_id
            WHERE eq.exam_id = %s
        """, (exam_id,))
        questions = cur.fetchall()
        conn.commit()
        return {"session_id": session_id, "exam_id": exam_id, "questions": questions}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error starting exam: {e}")
    finally:
        cur.close(); conn.close()

@router.post("/{session_id}/answers")
async def save_session_answers(
    session_id: int,
    # === BƯỚC 2: DÙNG MODEL LÀM TYPE HINT CHO PAYLOAD ===
    payload: SaveAnswersPayload, 
    user=Depends(get_current_user)
):
    """
    Lưu một danh sách các câu trả lời (tiến độ) vào CSDL.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Bạn có thể truy cập dữ liệu dễ dàng:
        if not payload.answers:
            return {"message": "Không có câu trả lời nào để lưu."}

        insert_data = []
        
        # 'payload.answers' bây giờ là một list các object SessionAnswerIn
        for answer in payload.answers:
            insert_data.append((
                session_id,
                answer.question_id,    # <--- Truy cập dữ liệu từ model
                answer.selected_option, # <--- Truy cập dữ liệu từ model
                False # Tạm thời chưa tính 'is_correct' ở đây
            ))

        # --- Chạy batch insert (nhớ sửa SQL cho phù hợp) ---
        sql_insert = """
            INSERT INTO SessionResults (session_id, question_id, selected_option, is_correct)
            VALUES (?, ?, ?, ?)
            ON DUPLICATE KEY UPDATE
                selected_option = VALUES(selected_option)
        """
        
        cur.executemany(sql_insert, insert_data)
        conn.commit()
        
        return {
            "message": "Đã lưu thành công " + str(len(insert_data)) + " câu trả lời.",
            "session_id": session_id
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu câu trả lời: {str(e)}")
    finally:
        cur.close()
        conn.close()

@router.post("/{session_id}/submit")
async def submit_exam(session_id: int):
    """Submit exam and calculate score."""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT COUNT(*) AS total, SUM(is_correct) AS correct
            FROM SessionResults
            WHERE session_id = %s
        """, (session_id,))
        stats = cur.fetchone()
        total = stats["total"] or 0
        correct = stats["correct"] or 0
        score = int((correct / total) * 10) if total > 0 else 0

        cur.execute("""
            UPDATE ExamSessions
            SET end_time=NOW(), total_score=%s
            WHERE session_id=%s
        """, (score, session_id))
        conn.commit()
        return {
            "session_id": session_id,
            "total_questions": total,
            "correct": correct,
            "wrong": total - correct,
            "total_score": score
        }
    finally:
        cur.close(); conn.close()

@router.get("/{session_id}/results")
async def get_exam_results(session_id: int):
    """Get session results."""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT q.question_text, q.options, q.answer_letter,
                   r.selected_option, r.is_correct
            FROM SessionResults r
            JOIN Questions q ON r.question_id = q.question_id
            WHERE r.session_id=%s
        """, (session_id,))
        return cur.fetchall()
    finally:
        cur.close(); conn.close()
