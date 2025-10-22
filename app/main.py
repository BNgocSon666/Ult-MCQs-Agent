from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body
from typing import Any, Dict
from .tools import extract_and_clean_from_uploadfile, save_json_to_disk
from .agent import Agent, SummaryMode
import tempfile
import os
from .tools import extract_text_from_audio_with_gemini, extract_transcript_from_audio_with_gemini

app = FastAPI(title="Ultimate MCQs Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = Agent()

@app.get('/')
async def health():
    return {"status": "ok", "description": "Ultimate MCQ Agent is running"}

@app.post("/agent/text")
async def run_agent_text(
    file: UploadFile,
    num_questions: int = Form(5),
    summary_mode: SummaryMode = Form(SummaryMode.AUTO)
):
    """
    Nhận file văn bản (txt, pdf, docx) → đọc nội dung → tóm tắt/sinh câu hỏi theo chế độ.
    \nsummary_mode: "auto" → Tự động sinh tóm tắt nếu nội dung dài.
    \nsummary_mode: "force" → Luôn tóm tắt trước khi sinh câu hỏi.
    \nsummary_mode: "none" → Không tóm tắt.
    """
    try:
        ok, text = await extract_and_clean_from_uploadfile(file)
        if not ok:
            raise HTTPException(status_code=400, detail=text)

        result = agent.decide_and_run(
            text,
            num_questions=num_questions,
            summary_mode=summary_mode
        )

        return {"filename": file.filename, "result": result}
    except Exception as e:
        return {"error": str(e)}

@app.post("/agent/audio")
async def run_agent_audio(
    file: UploadFile,
    num_questions: int = Form(5),
    summary_mode: SummaryMode = Form(SummaryMode.AUTO)
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
            is_summary=False
        )

        os.remove(tmp_path)
        return {
            "filename": file.filename,
            "transcript": transcript,
            "summary_from_audio": summary_from_audio,
            "result": result
        }

    except Exception as e:
        return {"error": str(e)}

@app.post('/agent/save')
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
