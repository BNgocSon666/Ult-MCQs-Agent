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

            # Gói text và options thành JSON string
            question_text_json_str = json.dumps(question_text, ensure_ascii=False)
            options_json_str = json.dumps(options_list, ensure_ascii=False)

            call_sp_save_question(
                source_file_id=file_id,
                creator_id=user_id,
                question_text=question_text_json_str,
                options_json=options_json_str,
                answer_letter=str(answer_letter)[:1], # Đảm bảo 1 ký tự
                status=str(status)[:20] # Đảm bảo vừa cột (VARCHAR 20)
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
