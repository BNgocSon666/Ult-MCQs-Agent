from fastapi import Body, FastAPI, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os, json
import tempfile
from typing import Any, Dict
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from .auth import router as auth_router
from .config import JWT_SECRET_KEY, JWT_ALGORITHM
from .agent import Agent, SummaryMode
from .db import call_sp_save_file, call_sp_save_question
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

        result = agent.decide_and_run(
            text, num_questions=num_questions, summary_mode=summary_mode
        )
        filename = file.filename
        suffix = os.path.splitext(filename)[1].lower().lstrip(".") or "txt"
        file_type = suffix.upper()
        summary = None
        if isinstance(result, dict):
            summary = result.get("summary")

        filename_json_str = json.dumps(filename, ensure_ascii=False)

        file_id = call_sp_save_file(
            uploader_id=user["user_id"],
            filename=filename_json_str,
            file_type=file_type,
            storage_path=None,
            raw_text=text,
            summary=summary
        )
        if not file_id:
            raise HTTPException(status_code=500, detail="Không lấy được file_id sau khi gọi sp_SaveFile.")

        # 4️⃣ Lưu từng CÂU HỎI
        questions = []
        if isinstance(result, dict):
            questions = result.get("questions", []) or []
        elif isinstance(result, list):
            questions = result

        saved = 0
        for q in questions:
            question_text = q.get("question") or q.get("question_text") or ""
            options_list = q.get("options") or []
            answer_letter = q.get("answer_letter") or q.get("answer") or ""
            status = q.get("status") or "TEMP"

            options_json_str = json.dumps(options_list, ensure_ascii=False)
            question_text_json_str = json.dumps(question_text, ensure_ascii=False)

            call_sp_save_question(
                source_file_id=file_id,
                creator_id=user["user_id"],
                question_text=question_text_json_str,
                options_json=options_json_str,
                answer_letter=str(answer_letter)[:1],
                status=status
            )
            saved += 1

        # 5️⃣ Trả kết quả cho client
        return {
            "message": "✅ Sinh và lưu dữ liệu thành công.",
            "file_id": file_id,
            "saved_questions": saved,
            "result_preview": result.get("summary", "") if isinstance(result, dict) else None
        }

    except HTTPException:
        raise
        # return {"filename": file.filename, "result": result}
    except Exception as e:
        return {"error": str(e)}

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
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # 1️⃣ Lấy transcript đầy đủ
        transcript = extract_transcript_from_audio_with_gemini(tmp_path)

        # ⚠️ HIỂN THỊ LỖI CHI TIẾT
        if transcript and transcript.startswith("[Lỗi"):
            # Trả về thông báo lỗi chi tiết từ tools.py
            os.remove(tmp_path)
            return {"error": transcript}

        if not transcript:
            # Chỉ hiển thị lỗi chung nếu transcript thực sự rỗng (không có lỗi chi tiết)
            os.remove(tmp_path)
            return {"error": "Không thể chép lại nội dung ghi âm (transcript rỗng)."}

        # 2️⃣ Tóm tắt nội dung (Giữ nguyên logic kiểm tra)
        summary_from_audio = extract_text_from_audio_with_gemini(tmp_path)
        if summary_from_audio and summary_from_audio.startswith("[Lỗi"):
            # Nếu tóm tắt lỗi, hiển thị lỗi chi tiết
            return {"error": summary_from_audio, "transcript": transcript}

        # 3️⃣ Sinh câu hỏi từ transcript
        result = agent.decide_and_run(
            transcript,
            num_questions=num_questions,
            summary_mode=summary_mode,
            is_summary=False,
        )

        os.remove(tmp_path)
        return {
            "filename": file.filename,
            "transcript": transcript,
            "summary_from_audio": summary_from_audio,
            "result": result,
        }

    except Exception as e:
        return {"error": str(e)}

@app.post("/agent/save")
async def save_agent_result(filename: str = Form(...), result: Dict[str, Any] = Body(...)):
    """Save a previously returned agent result to disk.

    Accepts a `filename` (string) and the `result` JSON body. Returns the
    saved path on success.
    """

    if not filename:
        raise HTTPException(status_code=400, detail="filename is required")

    try:
        out_path = save_json_to_disk(result, filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to save file: {e}")

    return {"saved_to": out_path}
