import tempfile
import os
from typing import Tuple
import fitz
from docx import Document
from .utils import clean_text, check_file_size_bytes, safe_filename
from .config import GOOGLE_API_KEY, MAX_FILE_SIZE_MB
import google.generativeai as genai_old
import json
import hashlib
from google import genai

EVAL_CACHE = {}

if GOOGLE_API_KEY:
    genai_old.configure(api_key=GOOGLE_API_KEY)

client = genai.Client(api_key=GOOGLE_API_KEY)

def extract_text_from_pdf_bytes(content: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    text = ""
    try:
        with fitz.open(tmp_path) as pdf:
            for page in pdf:
                text += page.get_text()
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
    return text

def extract_text_from_docx_bytes(content: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    text = ""
    try:
        doc = Document(tmp_path)
        text = '\n'.join([p.text for p in doc.paragraphs])
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
    return text

def extract_text_from_txt_bytes(content: bytes) -> str:
    return content.decode('utf-8', errors='ignore')

async def extract_and_clean_from_uploadfile(upload_file) -> Tuple[bool, str]:
    raw = await upload_file.read()
    ok, msg = check_file_size_bytes(raw, MAX_FILE_SIZE_MB)
    if not ok:
        return False, msg

    suffix = os.path.splitext(safe_filename(upload_file.filename))[1].lower()
    if suffix == '.pdf':
        text = extract_text_from_pdf_bytes(raw)
    elif suffix in ('.doc', '.docx'):
        text = extract_text_from_docx_bytes(raw)
    elif suffix == '.txt':
        text = extract_text_from_txt_bytes(raw)
    else:
        return False, 'Định dạng không hỗ trợ. Hỗ trợ: PDF, DOCX, TXT.'

    cleaned = clean_text(text)
    if not cleaned:
        return False, 'Không thể trích xuất nội dung từ file (file rỗng hoặc lỗi).'
    return True, cleaned

def call_gemini_summarize(text: str, model_name: str = "gemini-2.5-flash") -> str:
    model = genai_old.GenerativeModel(model_name, tools=[])
    # Yêu cầu model tự phát hiện ngôn ngữ đầu vào và trả về bản tóm tắt bằng cùng ngôn ngữ
    prompt = (
        "Hãy phát hiện ngôn ngữ của văn bản dưới đây. Sau đó tạo một bản tóm tắt ngắn gọn, rõ ràng và đầy đủ bằng cùng một ngôn ngữ.\n"
        f"Nội dung:\n{text}"
    )
    resp = model.generate_content([prompt])
    return resp.text.strip()

def call_gemini_generate_mcqs(text: str, num_questions: int = 5, model_name: str = "gemini-2.5-flash") -> list:
    model = genai_old.GenerativeModel(model_name, tools=[])
    # Yêu cầu model phát hiện ngôn ngữ đầu vào và sinh câu hỏi trắc nghiệm bằng cùng ngôn ngữ
    prompt = f"""
    Bạn là hệ thống AI chuyên sinh câu hỏi trắc nghiệm.
    Trước tiên hãy xác định ngôn ngữ của văn bản dưới đây. Sau đó phân tích và sinh ra **{num_questions} câu hỏi trắc nghiệm có 4 lựa chọn** sử dụng **chính ngôn ngữ của văn bản đó**, trong đó chỉ **một lựa chọn là đúng**.

    ---

    📘 **Ngữ cảnh gốc (KHÔNG tóm tắt, KHÔNG cắt ngắn):**
    {text}

    ---

    **Hướng dẫn chi tiết:**
    1. Xác định **loại tài liệu** (ví dụ: học thuật, kỹ thuật, pháp luật, giáo dục, mô tả dự án,...).  
    2. Sinh câu hỏi phù hợp phong cách đó.  
    3. Mỗi câu hỏi phải:
        - Context không phải là toàn bộ đoạn văn, mà là phần liên quan trực tiếp đến câu hỏi, dài 2-3 câu.
        - Phản ánh đúng thông tin trong context (không suy diễn).
        - Có 1 đáp án đúng rõ ràng, 3 đáp án nhiễu cùng chủ đề.
        - Không hỏi trùng ý hoặc trùng dữ kiện.
        - Câu hỏi và đáp án phải cùng ngôn ngữ với văn bản gốc.
    4. Distractors phải hợp lý — cùng phạm trù, không quá sai.
    5. Nếu nội dung context chỉ đủ cho 1-2 câu hỏi, trả ít hơn — không bịa thêm.

    ---

    **Định dạng đầu ra JSON (duy nhất, không có văn bản nào khác):**
    [
    {{
        "context": "Đoạn văn bản liên quan đến câu hỏi (giữ nguyên, không tóm tắt).",
        "question": "Câu hỏi trắc nghiệm tiếng Việt rõ ràng, có một đáp án đúng duy nhất.",
        "options": [
            "A. Đáp án thứ nhất",
            "B. Đáp án thứ hai",
            "C. Đáp án thứ ba",
            "D. Đáp án thứ tư"
        ],
        "answer_letter": "B"
    }},
    ...
    ]

    **Lưu ý bắt buộc:**
    - KHÔNG chèn markdown hoặc ```json.  
    - Nếu không thể tạo hợp lệ, trả về `[]`.  
    - Giữ nguyên văn context, không được tóm tắt hay cắt ngắn.
    """

    resp = model.generate_content([prompt])
    mcq_text = resp.text.strip()

    if mcq_text.startswith("```json"):
        mcq_text = mcq_text[7:]
    if mcq_text.startswith("```"):
        mcq_text = mcq_text[3:]
    if mcq_text.endswith("```"):
        mcq_text = mcq_text[:-3]
    mcq_text = mcq_text.strip()

    try:
        data = json.loads(mcq_text)
    except Exception:
        data = [{
            "context": text[:200] + "...",
            "question": "Không thể tạo câu hỏi hợp lệ từ nội dung này.",
            "options": ["Lỗi", "Lỗi", "Lỗi", "Lỗi"],
            "answer": "A. Lỗi"
        }]
    return data

# tools.py
def extract_text_from_audio_with_gemini(file_path: str, model_name: str = "gemini-2.5-flash") -> str:
    """
    Dùng Gemini 2.5 (SDK mới) để tóm tắt audio mà không lỗi ragStoreName.
    """
    prompt = (
        "Hãy nghe kỹ nội dung trong đoạn ghi âm này, "
        "phát hiện ngôn ngữ được nói và tóm tắt lại ngắn gọn, rõ ràng, đầy đủ bằng chính ngôn ngữ đó."
    )
    try:
        uploaded_file = client.files.upload(file=file_path)
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, uploaded_file]
        )
        return response.text.strip()
    except Exception as e:
        return f"[Lỗi Gemini audio summarize] {str(e)}"


def extract_transcript_from_audio_with_gemini(file_path: str, model_name: str = "gemini-2.5-flash") -> str:
    """
    Dùng Gemini 2.5 (SDK mới) để chép lại transcript audio mà không lỗi ragStoreName.
    """
    prompt = (
        "Hãy nghe toàn bộ đoạn ghi âm này và chép lại nguyên văn nội dung nói ra, "
        "giữ nguyên ngôn ngữ gốc của người nói, không tóm tắt, không bỏ sót chi tiết."
    )
    try:
        uploaded_file = client.files.upload(file=file_path)
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, uploaded_file]
        )
        return response.text.strip()
    except Exception as e:
        return f"[Lỗi Gemini transcript] {str(e)}"

def save_json_to_disk(obj, filename: str) -> str:
    out_path = os.path.join(tempfile.gettempdir(), filename)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return out_path


def get_hash_key(context, question):
    # Ép toàn bộ phần tử về string, tránh lỗi tuple/bool/int
    def to_str(x):
        if isinstance(x, (list, tuple)):
            return " ".join(str(i) for i in x)
        return str(x)

    context_str = to_str(context)
    question_str = to_str(question)
    return hashlib.md5((context_str + question_str).encode("utf-8")).hexdigest()

def evaluate_mcq(mcq: dict, context_text: str = "") -> dict:
    global EVAL_CACHE
    key = get_hash_key(context_text, mcq.get("question", ""))
    if key in EVAL_CACHE:
        return EVAL_CACHE[key]

    question_data = [mcq]

    prompt = f"""
Bạn là chuyên gia có kinh nghiệm trong việc đánh giá chất lượng câu hỏi trắc nghiệm (MCQs).

Hãy chấm điểm từng câu hỏi theo 4 tiêu chí sau (tổng cộng 100 điểm):

1. **Accuracy (50 điểm)**  
- Độ chính xác của đáp án đúng so với nội dung gốc.  
- Đúng hoàn toàn → 50; Gần đúng → 30-45; Sai hoặc không có trong văn bản → 0-25.  

2. **Alignment (25 điểm)**  
- Mức độ bám sát trọng tâm nội dung.  
- Đúng trọng tâm → 20; Chi tiết phụ hoặc suy luận thêm → 5-15; Không liên quan → 0.  

3. **Distractors (20 điểm)**  
- Độ hợp lý của đáp án sai.  
- Hợp lý, cùng phạm trù → 18-20; Có 1-2 lựa chọn dễ loại → 10-17; Phần lớn vô lý → 0-9.  

4. **Clarity (5 điểm)**  
- Độ rõ ràng, ngữ pháp, mạch lạc.  
- 5: Rõ ràng, đúng ngữ pháp; 4: Hơi dài dòng; 3: Có lỗi nhỏ; 2: Sai cấu trúc; 1-0: Mơ hồ hoặc vô nghĩa. 

---

**Yêu cầu kết quả:**  
Chỉ trả về **một JSON hợp lệ duy nhất**, không có văn bản nào khác.

Cấu trúc JSON:
{{
  "overall_score": <điểm trung bình>,
  "details": [
    {{
      "question": "Câu hỏi",
      "scores": {{
        "accuracy": <0-50>,
        "alignment": <0-25>,
        "distractors": <0-20>,
        "clarity": <0-5>,
        "total": <tổng điểm>
      }},
      "status": "accepted | need_review | rejected"
    }}
  ]
}}

Quy tắc phân loại:
- total ≥ 80 → accepted  
- 60 ≤ total < 80 → need_review  
- total < 60 → rejected  

---

**Context (nội dung gốc):**
{context_text}

**Danh sách câu hỏi:**
{json.dumps(question_data, ensure_ascii=False, indent=2)}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()

        # Làm sạch output để parse JSON
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        data = json.loads(text)
        details = data.get("details", [{}])[0]
        scores = details.get("scores", {})
        total = scores.get("total", data.get("overall_score", 0))

        # Chuyển kết quả sang dạng giống cũ để tương thích hệ thống
        mcq_result = dict(mcq)
        mcq_result["score"] = int(total)
        mcq_result["status"] = details.get("status", "need_review")
        mcq_result["_eval_breakdown"] = {
            "accuracy": scores.get("accuracy", 0),
            "alignment": scores.get("alignment", 0),
            "distractors": scores.get("distractors", 0),
            "clarity": scores.get("clarity", 0),
        }

        EVAL_CACHE[key] = mcq_result
        return mcq_result

    except Exception as e:
        fallback = dict(mcq)
        fallback["score"] = 0
        fallback["status"] = "rejected"
        fallback["_eval_breakdown"] = {
            "accuracy": 0,
            "alignment": 0,
            "distractors": 0,
            "clarity": 0,
        }
        fallback["comment"] = f"Lỗi khi gọi Gemini: {str(e)}"
        return fallback
