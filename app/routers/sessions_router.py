from fastapi import APIRouter, Depends, Form, HTTPException
from ..db import get_connection
from .agent_router import get_current_user

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

@router.post("/{session_id}/answer")
async def answer_question(session_id: int, data: dict):
    """Record answer and check correctness."""
    question_id = data.get("question_id")
    selected_option = data.get("selected_option")
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT answer_letter FROM Questions WHERE question_id=%s", (question_id,))
        q = cur.fetchone()
        if not q:
            raise HTTPException(status_code=404, detail="Question not found.")

        is_correct = 1 if q["answer_letter"] == selected_option.upper() else 0
        cur.execute("""
            INSERT INTO SessionResults (session_id, question_id, selected_option, is_correct)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE selected_option=%s, is_correct=%s
        """, (session_id, question_id, selected_option, is_correct, selected_option, is_correct))
        conn.commit()
        return {"is_correct": bool(is_correct)}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving answer: {e}")
    finally:
        cur.close(); conn.close()

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
