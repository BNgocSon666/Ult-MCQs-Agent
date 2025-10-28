from fastapi import APIRouter, UploadFile, Form, HTTPException, Body, Depends
import os, json, tempfile
from typing import Any, Dict
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from ..agent import Agent, SummaryMode
from ..db import call_sp_save_file, call_sp_save_question_with_eval, get_connection
from ..tools import (
    extract_and_clean_from_uploadfile,
    extract_text_from_audio_with_gemini,
    extract_transcript_from_audio_with_gemini,
)
from ..config import JWT_SECRET_KEY, JWT_ALGORITHM

router = APIRouter(prefix="/agent", tags=["Agent"])

agent = Agent()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        username = payload.get("sub")
        is_admin = payload.get("is_admin", 0)
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT is_active FROM Users WHERE user_id=?", (user_id,))
        user = cur.fetchone()
        cur.close(); conn.close()

        if not user:
            raise HTTPException(status_code=401, detail="User not found.")
        if user["is_active"] == 0:
            raise HTTPException(status_code=403, detail="Account disabled.")

        return {"username": username, "user_id": user_id, "is_admin": is_admin}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

@router.post("/text")
async def run_agent_text(
    file: UploadFile,
    num_questions: int = Form(5),
    summary_mode: SummaryMode = Form(SummaryMode.AUTO),
    user=Depends(get_current_user)
):
    """Extract text from document -> summarize + generate questions."""
    try:
        ok, text = await extract_and_clean_from_uploadfile(file)
        if not ok:
            raise HTTPException(status_code=400, detail=text)

        result = agent.decide_and_run(text, num_questions=num_questions, summary_mode=summary_mode)
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
        raise HTTPException(status_code=500, detail=f"Agent text processing error: {str(e)}")

@router.post("/audio")
async def run_agent_audio(
    file: UploadFile,
    num_questions: int = Form(5),
    summary_mode: SummaryMode = Form(SummaryMode.AUTO),
    user=Depends(get_current_user)
):
    """Process audio: transcribe -> summarize -> generate MCQs."""
    try:
        suffix = os.path.splitext(file.filename)[1].lower()
        file_type = suffix.lstrip(".").upper() or "AUDIO"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # get transcript
        transcript = extract_transcript_from_audio_with_gemini(tmp_path)
        if transcript and transcript.startswith("[Lỗi"):
            os.remove(tmp_path)
            raise HTTPException(status_code=500, detail=transcript)
        if not transcript:
            os.remove(tmp_path)
            raise HTTPException(status_code=400, detail="Empty transcript.")

        # get summary directly from audio
        summary_from_audio = extract_text_from_audio_with_gemini(tmp_path)
        if summary_from_audio and summary_from_audio.startswith("[Lỗi"):
            print(f"Audio summary error: {summary_from_audio}")
            summary_from_audio = None

        # generate questions
        result = agent.decide_and_run(
            transcript,
            num_questions=num_questions,
            summary_mode=summary_mode,
            is_summary=False,
        )

        os.remove(tmp_path)

        # prepare result
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
            "raw_text": transcript,
            "summary": final_summary,
            "questions": questions,
            "_transcript": transcript,
            "_summary_from_audio": summary_from_audio,
            "_summary_from_transcript": summary_from_agent
        }

    except HTTPException:
        raise
    except Exception as e:
        os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=f"Agent audio processing error: {str(e)}")

@router.post("/save")
async def save_agent_result(
    payload: Dict[str, Any] = Body(...),
    user=Depends(get_current_user)
):
    """Save AI results (file + questions) to database."""
    try:
        filename = payload.get("filename")
        file_type = payload.get("file_type")
        raw_text = payload.get("raw_text")
        summary = payload.get("summary")
        questions = payload.get("questions", [])
        user_id = user["user_id"]

        if not all([filename, file_type, raw_text, user_id]):
            raise HTTPException(status_code=400, detail="Missing filename, file_type, raw_text or user info.")

        filename_json_str = json.dumps(filename, ensure_ascii=False)
        file_id = call_sp_save_file(
            uploader_id=user_id,
            filename=filename_json_str,
            file_type=str(file_type)[:50],
            storage_path=None,
            raw_text=raw_text,
            summary=summary
        )
        if not file_id:
            raise HTTPException(status_code=500, detail="File save failed (no file_id).")

        saved_count = 0
        if not isinstance(questions, list):
            questions = []

        for q in questions:
            if not isinstance(q, dict):
                continue

            question_text = q.get("question") or q.get("question_text") or "Invalid question"
            options_list = q.get("options") or []
            answer_letter = q.get("answer_letter") or q.get("answer") or "?"
            status = q.get("status") or "need_review"
            eval_info = q.get("_eval_breakdown", {}) or {}
            total_score = q.get("score", 0)
            accuracy_score = eval_info.get("accuracy", 0)
            alignment_score = eval_info.get("alignment", 0)
            distractors_score = eval_info.get("distractors", 0)
            clarity_score = eval_info.get("clarity", 0)
            status_by_agent = q.get("status", "need_review")

            call_sp_save_question_with_eval(
                source_file_id=file_id,
                creator_id=user_id,
                question_text=json.dumps(question_text, ensure_ascii=False),
                options_json=json.dumps(options_list, ensure_ascii=False),
                answer_letter=str(answer_letter)[:1],
                status=str(status)[:20],
                model_version="gemini-2.5-flash",
                total_score=int(total_score),
                accuracy_score=int(accuracy_score),
                alignment_score=int(alignment_score),
                distractors_score=int(distractors_score),
                clarity_score=int(clarity_score),
                status_by_agent=status_by_agent,
                raw_response_json=json.dumps(q, ensure_ascii=False)
            )
            saved_count += 1

        return {
            "message": "✅ Data saved successfully.",
            "file_id": file_id,
            "saved_questions": saved_count
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Critical save error /agent/save: {e}")
        raise HTTPException(status_code=500, detail=f"Server error while saving: {str(e)}")
