from fastapi import APIRouter, Depends, HTTPException, Form
from typing import Optional
from ..db import get_connection

# === IMPORT XÁC THỰC ===
# Import hàm xác thực TÙY CHỌN từ auth_router
from .auth_router import get_optional_current_user 

# === IMPORT PYDANTIC MODELS ===
# Giả sử bạn đã định nghĩa chúng trong 'schemas.py'
from ..schemas import SaveAnswersPayload 


router = APIRouter(prefix="/sessions", tags=["Sessions"])


# === ENDPOINT 1: BẮT ĐẦU (CHO CẢ KHÁCH VÀ USER) ===
@router.post("/start/{exam_id}")
async def start_exam_session(
    exam_id: int,
    user: Optional[dict] = Depends(get_optional_current_user), 
    guest_name: Optional[str] = Form(None)
):
    """
    Bắt đầu một phiên làm bài.
    - Nếu có 'user' (đã login), tạo session với user_id.
    - Nếu không có 'user' nhưng có 'guest_name', tạo session cho khách.
    """
    
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
            VALUES (?, ?, ?, NOW())
            """,
            (exam_id, current_user_id, current_guest_name)
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
        raise HTTPException(status_code=500, detail=f"Lỗi CSDL: {str(e)}")
    finally:
        cur.close()
        conn.close()


# === ENDPOINT 2: LƯU ĐÁP ÁN (KHÔNG CẦN XÁC THỰC) ===
@router.post("/{session_id}/answers")
async def save_session_answers(
    session_id: int,
    payload: SaveAnswersPayload # Nhận list câu trả lời
):
    """
    Lưu một danh sách các câu trả lời (tiến độ) vào CSDL.
    Endpoint này không cần xác thực user, chỉ cần session_id hợp lệ.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True) 
    
    try:
        if not payload.answers:
            return {"message": "Không có câu trả lời nào để lưu."}

        # Lấy đáp án đúng để tính 'is_correct' ngay khi lưu
        question_ids = [answer.question_id for answer in payload.answers]
        placeholders = ','.join(['?'] * len(question_ids))
        
        cur.execute(
            f"SELECT question_id, answer_letter FROM Questions WHERE question_id IN ({placeholders})",
            tuple(question_ids)
        )
        correct_answers_map = {
            row["question_id"]: row["answer_letter"] for row in cur.fetchall()
        }

        # Chuẩn bị dữ liệu để batch insert
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

        # Chạy batch insert
        sql_insert = """
            INSERT INTO SessionResults (session_id, question_id, selected_option, is_correct)
            VALUES (?, ?, ?, ?)
            ON DUPLICATE KEY UPDATE
                selected_option = VALUES(selected_option),
                is_correct = VALUES(is_correct)
        """
        
        cur = conn.cursor() 
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


# === ENDPOINT 3: NỘP BÀI (KHÔNG CẦN XÁC THỰC) ===
@router.post("/{session_id}/submit")
async def submit_exam_and_score(
    session_id: int,
):
    """
    "Chốt" bài thi: Đếm điểm từ SessionResults và cập nhật vào ExamSessions.
    Endpoint này không cần xác thực user, chỉ cần session_id hợp lệ.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Đếm tổng số câu trả lời đúng đã được lưu
        cur.execute(
            "SELECT COUNT(1) AS final_score FROM SessionResults WHERE session_id = ? AND is_correct = 1",
            (session_id,)
        )
        result = cur.fetchone()
        final_score = result["final_score"] if result else 0

        # Cập nhật điểm tổng và thời gian kết thúc
        cur.execute(
            "UPDATE ExamSessions SET end_time = NOW(), total_score = ? WHERE session_id = ?",
            (final_score, session_id)
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
        raise HTTPException(status_code=500, detail=f"Lỗi khi nộp bài: {str(e)}")
    finally:
        cur.close()
        conn.close()

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
