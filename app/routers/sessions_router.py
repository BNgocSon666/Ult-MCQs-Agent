from fastapi import APIRouter, Depends, HTTPException, Form
from typing import Optional
from ..db import get_connection

# === IMPORT XÁC THỰC ===
from .auth_router import get_optional_current_user 

# === IMPORT PYDANTIC MODELS ===
from ..schemas import SaveAnswersPayload 


router = APIRouter(prefix="/sessions", tags=["Sessions"])


# === ENDPOINT 1: BẮT ĐẦU (Sửa ? -> %s) ===
@router.post("/start/{exam_id}")
async def start_exam_session(
    exam_id: int,
    user: Optional[dict] = Depends(get_optional_current_user), 
    guest_name: Optional[str] = Form(None)
):
    current_user_id = None
    current_guest_name = None

    if user:
        current_user_id = user["user_id"]
    elif guest_name:
        current_guest_name = guest_name
    else:
        raise HTTPException(
            status_code=400, 
            detail="Bạn phải đăng nhập hoặc cung cấp tên (guest_name) để làm bài."
        )

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO ExamSessions (exam_id, user_id, guest_name, start_time)
            VALUES (%s, %s, %s, NOW())
            """,
            (exam_id, current_user_id, current_guest_name) # <-- ĐÃ SỬA
        )
        new_session_id = cur.lastrowid
        conn.commit()
        
        return {
            "message": "Bắt đầu phiên làm bài thành công!",
            "session_id": new_session_id,
            "user_id": current_user_id,
            "guest_name": current_guest_name
        }
    except Exception as e:
        conn.rollback()
        print(f"LỖI NGHIÊM TRỌNG TẠI [tên_router]: {e}") 
        raise HTTPException(status_code=500, detail="Đã xảy ra lỗi máy chủ nội bộ.")
    finally:
        cur.close()
        conn.close()


# === ENDPOINT 2: LƯU ĐÁP ÁN (Sửa ? -> %s) ===
@router.post("/{session_id}/answers")
async def save_session_answers(
    session_id: int,
    payload: SaveAnswersPayload
):
    conn = get_connection()
    cur = conn.cursor(dictionary=True) 
    
    try:
        if not payload.answers:
            return {"message": "Không có câu trả lời nào để lưu."}

        question_ids = [answer.question_id for answer in payload.answers]
        placeholders = ','.join(['%s'] * len(question_ids)) # <-- ĐÃ SỬA
        
        cur.execute(
            f"SELECT question_id, answer_letter FROM Questions WHERE question_id IN ({placeholders})",
            tuple(question_ids)
        )
        correct_answers_map = {
            row["question_id"]: row["answer_letter"] for row in cur.fetchall()
        }

        insert_data = []
        for answer in payload.answers:
            correct_letter = correct_answers_map.get(answer.question_id)
            is_correct = (correct_letter is not None and correct_letter == answer.selected_option)
            
            insert_data.append((
                session_id,
                answer.question_id,
                answer.selected_option,
                is_correct
            ))

        sql_insert = """
            INSERT INTO SessionResults (session_id, question_id, selected_option, is_correct)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                selected_option = VALUES(selected_option),
                is_correct = VALUES(is_correct)
        """ # <-- ĐÃ SỬA
        
        cur = conn.cursor() 
        cur.executemany(sql_insert, insert_data)
        conn.commit()
        
        return {
            "message": "Đã lưu thành công " + str(len(insert_data)) + " câu trả lời.",
            "session_id": session_id
        }
    except Exception as e:
        conn.rollback()
        print(f"LỖI NGHIÊM TRỌNG TẠI [tên_router]: {e}") 
        raise HTTPException(status_code=500, detail="Đã xảy ra lỗi máy chủ nội bộ.")
    finally:
        cur.close()
        conn.close()


# === ENDPOINT 3: NỘP BÀI (Sửa ? -> %s) ===
@router.post("/{session_id}/submit")
async def submit_exam_and_score(
    session_id: int,
):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        cur.execute(
            "SELECT COUNT(1) AS final_score FROM SessionResults WHERE session_id = %s AND is_correct = 1",
            (session_id,) # <-- ĐÃ SỬA
        )
        result = cur.fetchone()
        final_score = result["final_score"] if result else 0

        cur.execute(
            "UPDATE ExamSessions SET end_time = NOW(), total_score = %s WHERE session_id = %s",
            (final_score, session_id) # <-- ĐÃ SỬA
        )
        
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Session không tồn tại hoặc không thể cập nhật.")

        conn.commit()
        
        return {
            "message": "Bài thi đã được nộp và chấm điểm thành công!",
            "session_id": session_id,
            "total_score": final_score
        }
    except Exception as e:
        conn.rollback()
        print(f"LỖI NGHIÊM TRỌNG TẠI [tên_router]: {e}") 
        raise HTTPException(status_code=500, detail="Đã xảy ra lỗi máy chủ nội bộ.")
    finally:
        cur.close()
        conn.close()

# === ENDPOINT 4: XEM KẾT QUẢ (File gốc của bạn đã đúng) ===
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


# === ENDPOINT 5: TẢI CÂU HỎI (Sửa ? -> %s) ===
@router.get("/{session_id}/questions")
async def get_session_questions(session_id: int):
    """
    Lấy toàn bộ câu hỏi cho một phiên làm bài.
    """
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        # 1. Lấy exam_id từ session_id
        cur.execute("SELECT exam_id FROM ExamSessions WHERE session_id = %s", (session_id,)) # <-- ĐÃ SỬA
        session = cur.fetchone()
        if not session:
            raise HTTPException(status_code=404, detail="Phiên làm bài không tồn tại.")
        
        exam_id = session["exam_id"]

        # 2. Lấy tất cả câu hỏi của exam_id đó
        cur.execute("""
            SELECT q.question_id, q.question_text, q.options
            FROM ExamQuestions eq
            JOIN Questions q ON eq.question_id = q.question_id
            WHERE eq.exam_id = %s
            ORDER BY eq.order_index ASC 
        """, (exam_id,)) # <-- ĐÃ SỬA
        
        questions = cur.fetchall()
        return {"session_id": session_id, "exam_id": exam_id, "questions": questions}
    
    except Exception as e:
        print(f"LỖI NGHIÊM TRỌNG TẠI [tên_router]: {e}") 
        raise HTTPException(status_code=500, detail="Đã xảy ra lỗi máy chủ nội bộ.")
    finally:
        cur.close(); conn.close()