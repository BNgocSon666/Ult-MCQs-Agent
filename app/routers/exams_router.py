from fastapi import APIRouter, Form, Depends, HTTPException
from ..db import get_connection
from .agent_router import get_current_user
import secrets

router = APIRouter(prefix="/exams", tags=["Exams"])

@router.post("/")
async def create_exam(
    title: str = Form(...),
    description: str = Form(""),
    question_ids: str = Form(...),
    user=Depends(get_current_user)
):
    """Create exam and generate unique share token."""
    conn = get_connection(); cur = conn.cursor()
    try:
        ids = [int(x.strip()) for x in question_ids.split(",") if x.strip().isdigit()]
        share_token = secrets.token_hex(8)  # generate 16-char unique token

        # ensure uniqueness (in rare case of collision)
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
        raise HTTPException(status_code=500, detail=f"Error creating exam: {e}")
    finally:
        cur.close(); conn.close()

@router.get("/")
async def get_exams(user=Depends(get_current_user)):
    """Get all exams created by current user."""
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
    """Get exam info with question list."""
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
    """Delete exam."""
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Exams WHERE exam_id=%s AND creator_id=%s", (exam_id, user["user_id"]))
        affected = cur.rowcount
        conn.commit()
        if affected == 0:
            raise HTTPException(status_code=404, detail="Exam not found.")
        return {"message": "🗑️ Exam deleted successfully."}
    finally:
        cur.close(); conn.close()
