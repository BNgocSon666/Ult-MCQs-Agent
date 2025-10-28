from fastapi import Body, FastAPI, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os, json
import tempfile
from typing import Any, Dict
from fastapi import Depends, Path
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from .auth import router as auth_router
from .config import JWT_SECRET_KEY, JWT_ALGORITHM
from .agent import Agent, SummaryMode
from .db import call_sp_save_file, call_sp_save_question_with_eval, get_connection
from .tools import (
    extract_and_clean_from_uploadfile,
    extract_text_from_audio_with_gemini,
    extract_transcript_from_audio_with_gemini,
    save_json_to_disk,
)

app = FastAPI(title="Ultimate MCQs Agent", version="1.0.0", description="AI Agent for generating multiple-choice questions (MCQs) from text and audio inputs.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

agent = Agent()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return {"username": payload.get("sub"), "user_id": payload.get("user_id")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ hoặc đã hết hạn")

@app.get("/")
async def health():
    return {"status": "ok", "description": "Ultimate MCQ Agent is running"}

@app.post("/agent/text")
async def run_agent_text(
    file: UploadFile,
    num_questions: int = Form(5),
    summary_mode: SummaryMode = Form(SummaryMode.AUTO),
    user=Depends(get_current_user)
):
    """
    Nhận file văn bản (txt, pdf, docx) → đọc nội dung → tóm tắt/sinh câu hỏi theo chế độ.

    summary_mode: "auto" → Tự động sinh tóm tắt nếu nội dung dài.
    summary_mode: "force" → Luôn tóm tắt trước khi sinh câu hỏi.
    summary_mode: "none" → Không tóm tắt.
    """

    try:
        ok, text = await extract_and_clean_from_uploadfile(file)
        if not ok:
            raise HTTPException(status_code=400, detail=text)

        # 1️⃣ Chạy Agent
        result = agent.decide_and_run(
            text, num_questions=num_questions, summary_mode=summary_mode
        )
        
        # 2️⃣ Chuẩn bị dữ liệu trả về
        filename = file.filename
        suffix = os.path.splitext(filename)[1].lower().lstrip(".") or "txt"
        file_type = suffix.upper()
        
        summary = None
        questions = []
        if isinstance(result, dict):
            summary = result.get("summary")
            questions = result.get("questions", []) or []
        elif isinstance(result, list):
            questions = result

        # 3️⃣ Trả kết quả thô cho client
        return {
            "filename": filename,
            "file_type": file_type,
            "raw_text": text,
            "summary": summary,
            "questions": questions
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý agent/text: {str(e)}")

@app.post("/agent/audio")
async def run_agent_audio(
    file: UploadFile,
    num_questions: int = Form(5),
    summary_mode: SummaryMode = Form(SummaryMode.AUTO),
    user=Depends(get_current_user)
):
    """
    Nhận file âm thanh (mp3, wav, m4a) → Gemini nghe & chép lại (transcript) + tóm tắt → sinh câu hỏi.
    """

    try:
        suffix = os.path.splitext(file.filename)[1].lower()
        file_type = suffix.lstrip(".").upper() or "AUDIO"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # 1️⃣ Lấy transcript đầy đủ
        transcript = extract_transcript_from_audio_with_gemini(tmp_path)
        if transcript and transcript.startswith("[Lỗi"):
            os.remove(tmp_path)
            raise HTTPException(status_code=500, detail=transcript)
        if not transcript:
            os.remove(tmp_path)
            raise HTTPException(status_code=400, detail="Không thể chép lại nội dung ghi âm (transcript rỗng).")

        # 2️⃣ Tóm tắt nội dung (lấy bản tóm tắt trực tiếp từ audio)
        summary_from_audio = extract_text_from_audio_with_gemini(tmp_path)
        if summary_from_audio and summary_from_audio.startswith("[Lỗi"):
             # Nếu tóm tắt lỗi, vẫn tiếp tục nhưng báo lỗi này
            print(f"Lỗi khi tóm tắt audio: {summary_from_audio}")
            summary_from_audio = None # Không dùng bản tóm tắt này

        # 3️⃣ Sinh câu hỏi từ transcript
        # Agent có thể tạo ra 1 bản tóm tắt khác (từ transcript)
        result = agent.decide_and_run(
            transcript,
            num_questions=num_questions,
            summary_mode=summary_mode,
            is_summary=False,
        )

        os.remove(tmp_path)

        # 4️⃣ Chuẩn bị dữ liệu trả về
        # Ưu tiên summary do agent tạo ra (vì MCQs dựa trên nó)
        # Nếu không có, dùng summary trực tiếp từ audio
        summary_from_agent = None
        questions = []
        if isinstance(result, dict):
            summary_from_agent = result.get("summary")
            questions = result.get("questions", []) or []
        elif isinstance(result, list):
            questions = result

        final_summary = summary_from_agent if summary_from_agent else summary_from_audio

        return {
            "filename": file.filename,
            "file_type": file_type,
            "raw_text": transcript, # "raw_text" của file audio chính là transcript
            "summary": final_summary, # Summary để lưu vào DB
            "questions": questions,
            "_transcript": transcript,
            "_summary_from_audio": summary_from_audio, # Gửi thêm để client tham khảo
            "_summary_from_transcript": summary_from_agent # Gửi thêm để client tham khảo
        }

    except HTTPException:
        raise
    except Exception as e:
        os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý agent/audio: {str(e)}")

@app.post("/agent/save")
async def save_agent_result(
    payload: Dict[str, Any] = Body(...),
    user=Depends(get_current_user) # BẮT BUỘC: Thêm xác thực
):
    """
    Nhận kết quả (JSON) từ client (đã được xử lý bởi /agent/text hoặc /agent/audio)
    và LƯU vào cơ sở dữ liệu.
    """

    try:
        # 1️⃣ Lấy dữ liệu từ payload
        filename = payload.get("filename")
        file_type = payload.get("file_type")
        raw_text = payload.get("raw_text")
        summary = payload.get("summary")
        questions = payload.get("questions", [])
        user_id = user["user_id"]

        if not all([filename, file_type, raw_text, user_id]):
            raise HTTPException(status_code=400, detail="Thiếu thông tin filename, file_type, raw_text hoặc user.")

        # 2️⃣ Lưu FILE
        # Gói filename thành JSON string theo yêu cầu của procedure
        filename_json_str = json.dumps(filename, ensure_ascii=False)

        file_id = call_sp_save_file(
            uploader_id=user_id,
            filename=filename_json_str,
            file_type=str(file_type)[:50], # Đảm bảo không quá 50 char
            storage_path=None, # Ta không lưu file vật lý, chỉ lưu text
            raw_text=raw_text,
            summary=summary
        )
        if not file_id:
            raise HTTPException(status_code=500, detail="Không lấy được file_id sau khi gọi sp_SaveFile.")

        # 3️⃣ Lưu từng CÂU HỎI
        saved_count = 0
        if not isinstance(questions, list):
            questions = []

        for q in questions:
            if not isinstance(q, dict):
                continue # Bỏ qua nếu dữ liệu câu hỏi không hợp lệ

            question_text = q.get("question") or q.get("question_text") or "Câu hỏi bị lỗi"
            options_list = q.get("options") or []
            answer_letter = q.get("answer_letter") or q.get("answer") or "?"
            status = q.get("status") or "need_review" # Lấy status từ agent
            eval_info = q.get("_eval_breakdown", {}) or {}
            total_score = q.get("score", 0)
            accuracy_score = eval_info.get("accuracy", 0)
            alignment_score = eval_info.get("alignment", 0)
            distractors_score = eval_info.get("distractors", 0)
            clarity_score = eval_info.get("clarity", 0)
            status_by_agent = q.get("status", "need_review")

            # Gói text và options thành JSON string
            question_text_json_str = json.dumps(question_text, ensure_ascii=False)
            raw_response_json = json.dumps(q, ensure_ascii=False)
            options_json_str = json.dumps(options_list, ensure_ascii=False)

            call_sp_save_question_with_eval(
                source_file_id=file_id,
                creator_id=user_id,
                question_text=question_text_json_str,
                options_json=options_json_str,
                answer_letter=str(answer_letter)[:1],
                status=str(status)[:20],
                model_version="gemini-2.5-flash",
                total_score=int(total_score),
                accuracy_score=int(accuracy_score),
                alignment_score=int(alignment_score),
                distractors_score=int(distractors_score),
                clarity_score=int(clarity_score),
                status_by_agent=status_by_agent,
                raw_response_json=raw_response_json
            )
            saved_count += 1

        # 4️⃣ Trả kết quả
        return {
            "message": "✅ Lưu dữ liệu thành công.",
            "file_id": file_id,
            "saved_questions": saved_count
        }
    
    except HTTPException:
        raise
    except Exception as e:
        # Ghi log lỗi chi tiết
        print(f"LỖI NGHIÊM TRỌNG /agent/save: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ khi lưu: {str(e)}")

@app.get("/questions")
async def get_questions(file_id: int | None = None, user=Depends(get_current_user)):
    """Lấy danh sách câu hỏi (toàn bộ hoặc theo file_id)."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
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
        cur.close()
        conn.close()


# ========================
# 📘 GET /questions/{id}
# ========================
@app.get("/questions/{question_id}")
async def get_question_detail(question_id: int = Path(...), user=Depends(get_current_user)):
    """Lấy chi tiết 1 câu hỏi (bao gồm evaluation)."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
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
            raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi.")
        return row
    finally:
        cur.close()
        conn.close()


# ========================
# ✏️ PUT /questions/{id}
# ========================
@app.put("/questions/{question_id}")
async def update_question(
    question_id: int = Path(...),
    question_text: str = Form(...),
    options_json: str = Form(...),
    answer_letter: str = Form(...),
    status: str = Form("TEMP"),
    user=Depends(get_current_user)
):
    """Cập nhật nội dung câu hỏi."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE Questions
            SET question_text = %s, options = %s, answer_letter = %s, status = %s, updated_at = NOW()
            WHERE question_id = %s AND creator_id = %s
        """, (question_text, options_json, answer_letter, status, question_id, user["user_id"]))
        conn.commit()
        if cur.rowcount == 0:
            # Kiểm tra lại xem câu hỏi có tồn tại không
            cur.execute("SELECT question_id FROM Questions WHERE question_id=%s AND creator_id=%s",
                        (question_id, user["user_id"]))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi để cập nhật.")
        return {"message": "✅ Cập nhật câu hỏi thành công."}
    finally:
        cur.close()
        conn.close()


# ========================
# ❌ DELETE /questions/{id}
# ========================
@app.delete("/questions/{question_id}")
async def delete_question(question_id: int, user=Depends(get_current_user)):
    """Xóa câu hỏi và bản đánh giá liên quan."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1️⃣ Xóa evaluation trước (nếu có)
        cur.execute("DELETE FROM QuestionEvaluations WHERE question_id=%s", (question_id,))

        # 2️⃣ Xóa question và ghi lại số dòng bị ảnh hưởng NGAY LẬP TỨC
        cur.execute("""
            DELETE FROM Questions
            WHERE question_id=%s AND creator_id=%s
        """, (question_id, user["user_id"]))
        affected_rows = cur.rowcount  # 🧠 Lưu trước khi commit

        conn.commit()

        # 3️⃣ Nếu không xóa được dòng nào, kiểm tra lại xem có tồn tại không
        if affected_rows == 0:
            cur.execute("SELECT question_id FROM Questions WHERE question_id=%s AND creator_id=%s",
                        (question_id, user["user_id"]))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi để xóa.")

        return {"message": "🗑️ Đã xóa câu hỏi và bản đánh giá liên quan thành công."}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa: {e}")
    finally:
        cur.close()
        conn.close()


@app.get("/evaluations/{evaluation_id}")
async def get_evaluation_detail(evaluation_id: int, user=Depends(get_current_user)):
    """Lấy chi tiết 1 bản đánh giá."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT e.*, q.question_text, q.question_id
            FROM QuestionEvaluations e
            JOIN Questions q ON e.question_id = q.question_id
            WHERE e.evaluation_id=%s AND q.creator_id=%s
        """, (evaluation_id, user["user_id"]))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Không tìm thấy bản đánh giá.")
        return row
    finally:
        cur.close()
        conn.close()


@app.put("/evaluations/{evaluation_id}")
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
    """Cập nhật bản đánh giá."""
    conn = get_connection()
    cur = conn.cursor()
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
            # Kiểm tra xem có tồn tại thật không
            cur.execute("""
                SELECT e.evaluation_id
                FROM QuestionEvaluations e
                JOIN Questions q ON e.question_id = q.question_id
                WHERE e.evaluation_id=%s AND q.creator_id=%s
            """, (evaluation_id, user["user_id"]))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Không tìm thấy bản đánh giá để cập nhật.")

        return {"message": "✅ Cập nhật bản đánh giá thành công."}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật: {e}")
    finally:
        cur.close()
        conn.close()


@app.delete("/evaluations/{evaluation_id}")
async def delete_evaluation(evaluation_id: int, user=Depends(get_current_user)):
    """Xóa 1 bản đánh giá."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            DELETE e FROM QuestionEvaluations e
            JOIN Questions q ON e.question_id = q.question_id
            WHERE e.evaluation_id=%s AND q.creator_id=%s
        """, (evaluation_id, user["user_id"]))
        affected_rows = cur.rowcount
        conn.commit()

        if affected_rows == 0:
            # Kiểm tra lại có tồn tại thật không
            cur.execute("""
                SELECT e.evaluation_id
                FROM QuestionEvaluations e
                JOIN Questions q ON e.question_id = q.question_id
                WHERE e.evaluation_id=%s AND q.creator_id=%s
            """, (evaluation_id, user["user_id"]))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Không tìm thấy bản đánh giá để xóa.")

        return {"message": "🗑️ Đã xóa bản đánh giá thành công."}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa: {e}")
    finally:
        cur.close()
        conn.close()
