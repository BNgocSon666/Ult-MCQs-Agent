from fastapi import APIRouter, Depends, HTTPException, Form
from ..db import get_connection
from .agent_router import get_current_user

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])

@router.get("/{evaluation_id}")
async def get_evaluation_detail(evaluation_id: int, user=Depends(get_current_user)):
    """Get a single evaluation."""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT e.*, q.question_text, q.question_id
            FROM QuestionEvaluations e
            JOIN Questions q ON e.question_id = q.question_id
            WHERE e.evaluation_id=%s AND q.creator_id=%s
        """, (evaluation_id, user["user_id"]))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Evaluation not found.")
        return row
    finally:
        cur.close(); conn.close()

@router.put("/{evaluation_id}")
async def update_evaluation(
    evaluation_id: int,
    total_score: int = Form(...),
    accuracy_score: int = Form(...),
    alignment_score: int = Form(...),
    distractors_score: int = Form(...),
    clarity_score: int = Form(...),
    status_by_agent: str = Form(...),
    user=Depends(get_current_user)
):
    """Update evaluation scores."""
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE QuestionEvaluations e
            JOIN Questions q ON e.question_id = q.question_id
            SET e.total_score=%s,
                e.accuracy_score=%s,
                e.alignment_score=%s,
                e.distractors_score=%s,
                e.clarity_score=%s,
                e.status_by_agent=%s,
                e.updated_at=NOW()
            WHERE e.evaluation_id=%s AND q.creator_id=%s
        """, (
            total_score, accuracy_score, alignment_score,
            distractors_score, clarity_score, status_by_agent,
            evaluation_id, user["user_id"]
        ))
        affected_rows = cur.rowcount
        conn.commit()

        if affected_rows == 0:
            cur.execute("""
                SELECT e.evaluation_id
                FROM QuestionEvaluations e
                JOIN Questions q ON e.question_id = q.question_id
                WHERE e.evaluation_id=%s AND q.creator_id=%s
            """, (evaluation_id, user["user_id"]))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Evaluation not found.")
        return {"message": "✅ Evaluation updated successfully."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Update error: {e}")
    finally:
        cur.close(); conn.close()

@router.delete("/{evaluation_id}")
async def delete_evaluation(evaluation_id: int, user=Depends(get_current_user)):
    """Delete evaluation."""
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            DELETE e FROM QuestionEvaluations e
            JOIN Questions q ON e.question_id = q.question_id
            WHERE e.evaluation_id=%s AND q.creator_id=%s
        """, (evaluation_id, user["user_id"]))
        affected_rows = cur.rowcount
        conn.commit()

        if affected_rows == 0:
            cur.execute("""
                SELECT e.evaluation_id
                FROM QuestionEvaluations e
                JOIN Questions q ON e.question_id = q.question_id
                WHERE e.evaluation_id=%s AND q.creator_id=%s
            """, (evaluation_id, user["user_id"]))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Evaluation not found.")
        return {"message": "🗑️ Evaluation deleted successfully."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Delete error: {e}")
    finally:
        cur.close(); conn.close()
