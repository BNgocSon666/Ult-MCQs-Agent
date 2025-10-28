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
        user_id = payload.get("user_id")
        username = payload.get("sub")
        is_admin = payload.get("is_admin", 0)

        # ✅ Kiểm tra trạng thái tài khoản
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT is_active FROM Users WHERE user_id=?", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            raise HTTPException(status_code=401, detail="User không tồn tại.")
        if user["is_active"] == 0:
            raise HTTPException(status_code=403, detail="Tài khoản đã bị vô hiệu hóa.")

        return {"username": username, "user_id": user_id, "is_admin": is_admin}

    except JWTError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ hoặc đã hết hạn.")

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

@app.get("/users/{user_id}")
async def get_user_detail(user_id: int, user=Depends(get_current_user)):
    """Xem thông tin user (chỉ admin hoặc chính user đó)."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        # Chỉ cho phép chính chủ hoặc admin
        if user["user_id"] != user_id and user.get("is_admin", 0) == 0:
            raise HTTPException(status_code=403, detail="Không có quyền xem thông tin user khác.")

        cur.execute("""
            SELECT user_id, username, email, is_active, created_at
            FROM Users
            WHERE user_id = %s
        """, (user_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
        return row
    finally:
        cur.close()
        conn.close()


@app.put("/users/{user_id}")
async def update_user(
    user_id: int,
    username: str = Form(None),
    email: str = Form(None),
    password: str = Form(None),
    is_active: int = Form(1),
    user=Depends(get_current_user)
):
    """Cập nhật thông tin user (chỉ admin hoặc chính user đó)."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # ✅ Kiểm tra quyền
        if user["user_id"] != user_id and user.get("is_admin", 0) == 0:
            raise HTTPException(status_code=403, detail="Không có quyền chỉnh sửa user khác.")

        # ✅ Hash lại mật khẩu nếu có
        password_hash = None
        if password:
            from passlib.hash import bcrypt
            password_hash = bcrypt.hash(password)

        # ✅ Tạo câu lệnh động
        fields, params = [], []
        if username:
            fields.append("username=%s")
            params.append(username)
        if email:
            fields.append("email=%s")
            params.append(email)
        if password_hash:
            fields.append("password_hash=%s")
            params.append(password_hash)
        fields.append("is_active=%s")
        params.append(is_active)
        params.extend([user_id])

        sql = f"UPDATE Users SET {', '.join(fields)} WHERE user_id=%s"
        cur.execute(sql, tuple(params))
        affected_rows = cur.rowcount
        conn.commit()

        # ✅ Kiểm tra kết quả
        if affected_rows == 0:
            cur.execute("SELECT user_id FROM Users WHERE user_id=%s", (user_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Không tìm thấy người dùng để cập nhật.")

        return {"message": "✅ Cập nhật thông tin user thành công."}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật: {e}")
    finally:
        cur.close()
        conn.close()


@app.put("/users/{user_id}/deactivate")
async def deactivate_user(user_id: int, user=Depends(get_current_user)):
    """Vô hiệu hóa user thay vì xóa (soft delete)."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Chỉ cho phép admin hoặc chính chủ
        if user["user_id"] != user_id and user.get("is_admin", 0) == 0:
            raise HTTPException(status_code=403, detail="Không có quyền vô hiệu hóa user khác.")

        cur.execute("UPDATE Users SET is_active=0 WHERE user_id=%s", (user_id,))
        affected_rows = cur.rowcount
        conn.commit()

        if affected_rows == 0:
            cur.execute("SELECT user_id FROM Users WHERE user_id=%s", (user_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Không tìm thấy user để vô hiệu hóa.")

        return {"message": "🚫 Đã vô hiệu hóa tài khoản thành công."}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi vô hiệu hóa: {e}")
    finally:
        cur.close()
        conn.close()

@app.put("/users/{user_id}/activate")
async def activate_user(user_id: int, user=Depends(get_current_user)):
    """Kích hoạt lại user."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        if user.get("is_admin", 0) == 0:
            raise HTTPException(status_code=403, detail="Chỉ admin mới được kích hoạt user khác.")

        cur.execute("UPDATE Users SET is_active=1 WHERE user_id=%s", (user_id,))
        conn.commit()

        return {"message": "✅ Đã kích hoạt lại tài khoản."}
    finally:
        cur.close()
        conn.close()


@app.post("/exams")
async def create_exam(
    title: str = Form(...),
    description: str = Form(""),
    question_ids: str = Form(...),  # ⚠️ đổi từ list[int] sang str
    user=Depends(get_current_user)
):
    """Tạo đề thi mới từ danh sách question_ids."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1️⃣ Tách chuỗi "55,56,61" → [55,56,61]
        ids = [int(x.strip()) for x in question_ids.split(",") if x.strip().isdigit()]

        # 2️⃣ Tạo đề thi
        cur.execute("""
            INSERT INTO Exams (title, description, owner_id, created_at)
            VALUES (%s, %s, %s, NOW())
        """, (title, description, user["user_id"]))
        exam_id = cur.lastrowid

        # 3️⃣ Thêm liên kết câu hỏi
        for qid in ids:
            cur.execute("INSERT INTO ExamQuestions (exam_id, question_id) VALUES (%s, %s)", (exam_id, qid))

        conn.commit()
        return {"exam_id": exam_id, "message": f"✅ Tạo đề thi thành công với {len(ids)} câu hỏi."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo đề thi: {e}")
    finally:
        cur.close()
        conn.close()


@app.get("/exams")
async def get_exams(user=Depends(get_current_user)):
    """Lấy danh sách tất cả đề thi của user."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT exam_id, title, description, created_at
            FROM Exams
            WHERE owner_id=%s
            ORDER BY created_at DESC
        """, (user["user_id"],))
        return {"exams": cur.fetchall()}
    finally:
        cur.close()
        conn.close()


@app.get("/exams/{exam_id}")
async def get_exam_detail(exam_id: int, user=Depends(get_current_user)):
    """Lấy thông tin đề thi + danh sách câu hỏi."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        # 1️⃣ Thông tin đề
        cur.execute("""
            SELECT * FROM Exams WHERE exam_id=%s AND owner_id=%s
        """, (exam_id, user["user_id"]))
        exam = cur.fetchone()
        if not exam:
            raise HTTPException(status_code=404, detail="Không tìm thấy đề thi.")

        # 2️⃣ Danh sách câu hỏi
        cur.execute("""
            SELECT q.question_id, q.question_text, q.options, q.answer_letter
            FROM ExamQuestions eq
            JOIN Questions q ON eq.question_id = q.question_id
            WHERE eq.exam_id = %s
        """, (exam_id,))
        exam["questions"] = cur.fetchall()
        return exam
    finally:
        cur.close()
        conn.close()


@app.delete("/exams/{exam_id}")
async def delete_exam(exam_id: int, user=Depends(get_current_user)):
    """Xóa đề thi (và các liên kết câu hỏi)."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Exams WHERE exam_id=%s AND creator_id=%s", (exam_id, user["user_id"]))
        affected = cur.rowcount
        conn.commit()
        if affected == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy đề thi để xóa.")
        return {"message": "🗑️ Đã xóa đề thi thành công."}
    finally:
        cur.close()
        conn.close()


@app.post("/exam_sessions/start")
async def start_exam(
    exam_id: int = Form(...),
    guest_name: str | None = Form(None),
    user=Depends(get_current_user)
):
    """Bắt đầu bài thi - tạo ExamSession và trả về danh sách câu hỏi."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        # 1️⃣ Tạo session mới
        user_id = user["user_id"] if user else None
        cur.execute("""
            INSERT INTO ExamSessions (exam_id, user_id, guest_name, start_time)
            VALUES (%s, %s, %s, NOW())
        """, (exam_id, user_id, guest_name))
        session_id = cur.lastrowid

        # 2️⃣ Lấy danh sách câu hỏi của đề
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
        raise HTTPException(status_code=500, detail=f"Lỗi khi bắt đầu bài thi: {e}")
    finally:
        cur.close()
        conn.close()


@app.post("/exam_sessions/{session_id}/answer")
async def answer_question(session_id: int, data: dict):
    """Ghi câu trả lời và kiểm tra đúng/sai."""
    question_id = data.get("question_id")
    selected_option = data.get("selected_option")

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        # 1️⃣ Lấy đáp án đúng
        cur.execute("SELECT answer_letter FROM Questions WHERE question_id=%s", (question_id,))
        q = cur.fetchone()
        if not q:
            raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi.")

        is_correct = 1 if q["answer_letter"] == selected_option.upper() else 0

        # 2️⃣ Lưu kết quả trả lời
        cur.execute("""
            INSERT INTO SessionResults (session_id, question_id, selected_option, is_correct)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE selected_option=%s, is_correct=%s
        """, (session_id, question_id, selected_option, is_correct, selected_option, is_correct))

        conn.commit()
        return {"is_correct": bool(is_correct)}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu câu trả lời: {e}")
    finally:
        cur.close()
        conn.close()


@app.post("/exam_sessions/{session_id}/submit")
async def submit_exam(session_id: int):
    """Nộp bài và chấm điểm."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
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

        # Cập nhật điểm tổng
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
        cur.close()
        conn.close()


@app.get("/exam_sessions/{session_id}/results")
async def get_exam_results(session_id: int):
    """Xem lại toàn bộ câu trả lời."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
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
        cur.close()
        conn.close()
