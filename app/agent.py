from enum import Enum
import time
from .tools import (
    call_gemini_summarize,
    call_gemini_generate_mcqs,
    evaluate_mcq,
)

class SummaryMode(str, Enum):
    AUTO = "auto"
    FORCE = "force"
    NONE = "none"

class Agent:
    def decide_and_run(
        self,
        text: str,
        num_questions: int = 5,
        summary_mode: str = SummaryMode.AUTO,
        is_summary: bool = False
    ):
        """
        Pipeline process:
        - If is_summary=True → text is already summarized, only generate MCQs.
        - If summary_mode="force" → always summarize.
        - If summary_mode="none" → no summarize.
        - If summary_mode="auto" → summarize if text length > 3000 chars.
        """

        # Input already summary (From audio transcript)
        if is_summary:
            mcqs = timed_step("Sinh câu hỏi", call_gemini_generate_mcqs, text, num_questions)
            return {"mode": "mcqs", "questions": mcqs}

        # Always summarize
        if summary_mode == SummaryMode.FORCE:
            summary = timed_step("Tóm tắt", call_gemini_summarize, text)
            mcqs = timed_step(
                "Sinh câu hỏi", call_gemini_generate_mcqs, summary, num_questions
            )
            evaluated = timed_step("Đánh giá", evaluate_mcq, mcqs, summary)
            return {
                "mode": "summary+mcqs",
                "summary": summary,
                "questions": evaluated,
            }

        # No summarize
        if summary_mode == SummaryMode.NONE:
            mcqs = timed_step("Sinh câu hỏi", call_gemini_generate_mcqs, text, num_questions)
            evaluated = timed_step("Đánh giá", evaluate_mcq, mcqs, text)
            return {"mode": "mcqs", "questions": evaluated}

        # Summarize if text length > 3000 chars.
        if len(text) > 3000:
            summary = timed_step("Tóm tắt", call_gemini_summarize, text)
            mcqs = timed_step(
                "Sinh câu hỏi", call_gemini_generate_mcqs, summary, num_questions
            )
            evaluated = timed_step("Đánh giá", evaluate_mcq, mcqs, summary)
            return {
                "mode": "summary+mcqs",
                "summary": summary,
                "questions": evaluated,
            }

        # Default: Short text > summarize
        mcqs = timed_step("Sinh câu hỏi", call_gemini_generate_mcqs, text, num_questions)
        evaluated = timed_step("Đánh giá", evaluate_mcq, mcqs, text)
        return {"mode": "mcqs", "questions": evaluated}

def timed_step(label, func, *args, **kwargs):
    start = time.time()
    print(f"⏱️  Bắt đầu {label}...")
    result = func(*args, **kwargs)
    print(f"✅ {label} xong trong {time.time() - start:.2f}s\n")
    return result