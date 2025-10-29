from fastapi import APIRouter, Depends, HTTPException, Form, Path
from ..db import get_connection
from .auth_router import get_current_user

router = APIRouter(prefix="/questions", tags=["Questions"])

@router.get("/")
async def get_questions(file_id: int | None = None, user=Depends(get_current_user)):
    """Get all questions or filter by file_id."""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        if file_id:
            cur.execute("""
                SELECT q.*, e.total_score, e.accuracy_score, e.alignment_score,
                       e.distractors_score, e.clarity_score, e.status_by_agent
                FROM Questions q
                LEFT JOIN QuestionEvaluations e ON q.latest_evaluation_id = e.evaluation_id
                WHERE q.source_file_id = %s AND q.creator_id = %s
                ORDER BY q.created_at DESC
            """, (file_id, user["user_id"]))
        else:
            cur.execute("""
                SELECT q.*, e.total_score, e.accuracy_score, e.alignment_score,
                       e.distractors_score, e.clarity_score, e.status_by_agent
                FROM Questions q
                LEFT JOIN QuestionEvaluations e ON q.latest_evaluation_id = e.evaluation_id
                WHERE q.creator_id = %s
                ORDER BY q.created_at DESC
            """, (user["user_id"],))
        data = cur.fetchall()
        return {"count": len(data), "questions": data}
    finally:
        cur.close(); conn.close()

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
