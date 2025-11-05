import datetime
from typing import List
from fastapi import APIRouter, Response
from pydantic import BaseModel, Field
from weasyprint import HTML
from fastapi import Depends, HTTPException
from ..db import get_connection
import re

router = APIRouter()

# ---- 1. Định nghĩa Pydantic Models cho dữ liệu đầu vào ----
# Đảm bảo cấu trúc JSON gửi lên được xác thực

class MCQItem(BaseModel):
    """Mô hình cho một câu hỏi trắc nghiệm"""
    question: str
    options: List[str]
    answer_letter: str 

class PDFExportRequest(BaseModel):
    """Mô hình cho dữ liệu yêu cầu xuất PDF"""
    exam_id: int = Field(description="ID của bài kiểm tra để lấy tiêu đề và câu hỏi")

# ---- 2. Hàm helper để chuyển MCQs thành HTML/CSS ----

def format_mcqs_to_html(exam_title: str, questions: List[dict]) -> str:
    """
    Hàm này nhận tiêu đề và danh sách câu hỏi (từ DB) và biến nó thành HTML.
    """
    
    css_style = """
    <style>
        @page { size: A4; margin: 2cm; }
        body { font-family: 'Helvetica', 'Arial', sans-serif; font-size: 12px; line-height: 1.6; color: #333; }
        h1 { font-size: 24px; text-align: center; color: #000; padding-bottom: 5px; margin-bottom: 25px; border-bottom: none; page-break-after: avoid; }
        h2 { font-size: 18px; color: #000; border-bottom: 2px solid #f0f0f0; padding-bottom: 5px; page-break-after: avoid; }
        .question-block { margin-bottom: 25px; padding-top: 10px; page-break-inside: avoid; }
        .question { font-weight: bold; font-size: 14px; margin-bottom: 8px; }
        .options { list-style-type: none; padding-left: 15px; }
        .options li { margin-bottom: 5px; }
        .correct-answer { font-weight: bold; color: #28a745; }
    </style>
    """
    
    # Bắt đầu xây dựng HTML
    html_content = f"<html><head><meta charset='UTF-8'>{css_style}</head><body>"
    
    # Sử dụng tiêu đề động
    html_content += f"<h1>{exam_title}</h1>"
    
    # Vòng lặp
    for i, q in enumerate(questions): 
        html_content += f"<div class='question-block'>"
        # SỬA Ở ĐÂY: Dùng q['question_text'] thay vì q.question
        html_content += f"<p class='question'>Câu {i + 1}: {q.get('question_text', 'Lỗi câu hỏi')}</p>"
        
        html_content += "<ul class='options'>"

        # SỬA Ở ĐÂY: q['answer_letter'] và q['options']
        answer_letter = q.get('answer_letter', '?')
        options_list = q.get('options', [])
        
        # Đảm bảo options_list là một list (vì nó có thể là JSON string từ DB)
        import json
        if isinstance(options_list, str):
            try:
                options_list = json.loads(options_list)
            except:
                options_list = []

        answer_prefix = answer_letter + "." 
        
        for opt in options_list:
            if opt.strip().startswith(answer_prefix): 
                html_content += f"<li class='correct-answer'>- {opt}</li>" 
            else:
                html_content += f"<li>- {opt}</li>"
        
        html_content += "</ul>"
        html_content += "</div>"
        
    html_content += "</body></html>"
    return html_content

# ---- 3. Endpoint API để xuất PDF ----

@router.post(
    "/export/pdf",
    tags=["Export"],
    summary="Xuất một bài Exam (gồm câu hỏi) ra file PDF"
)
def export_to_pdf(
    data: PDFExportRequest,
    conn=Depends(get_connection) # <-- Thêm kết nối DB
):
    """
    Nhận một 'exam_id', tự động tìm tiêu đề và câu hỏi từ DB,
    và trả về một file PDF.
    """
    cur = conn.cursor(dictionary=True) # <-- Dùng cursor dictionary
    try:
        # 1. Lấy thông tin Exam (giống hệt exams_router.py)
        cur.execute(
            "SELECT title FROM Exams WHERE exam_id = %s", 
            (data.exam_id,)
        )
        exam = cur.fetchone()
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found.")
        
        exam_title = exam.get('title', 'Báo cáo Câu hỏi') # Lấy tiêu đề

        # 2. Lấy danh sách câu hỏi (giống hệt exams_router.py)
        cur.execute("""
            SELECT q.question_id, q.question_text, q.options, q.answer_letter
            FROM ExamQuestions eq
            JOIN Questions q ON eq.question_id = q.question_id
            WHERE eq.exam_id = %s
        """, (data.exam_id,))
        
        questions = cur.fetchall()
        if not questions:
            raise HTTPException(status_code=400, detail="Không có câu hỏi nào trong Exam này để xuất.")

        # 3. Định dạng dữ liệu thành HTML
        html_string = format_mcqs_to_html(exam_title, questions)
        
        # 4. Chuyển đổi HTML sang PDF
        pdf_bytes = HTML(string=html_string).write_pdf()
        
        # --- (5) ĐÃ SỬA TÊN FILE Ở ĐÂY ---
        
        # Làm sạch title để dùng làm tên file
        # Xóa các ký tự không hợp lệ
        safe_title = re.sub(r'[\\/*?:"<>|]', "", exam_title) 
        # Thay thế khoảng trắng bằng gạch dưới
        safe_title = re.sub(r'\s+', '_', safe_title).strip('._')
        # Giới hạn 50 ký tự đầu
        safe_title = safe_title[:50]

        # Fallback nếu title rỗng hoặc toàn ký tự đặc biệt
        if not safe_title:
            safe_title = f"Exam_{data.exam_id}"

        # Đổi định dạng timestamp thành DD-MM-YYYY
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y")
        # Đổi tên file thành TenFile-DD-MM-YYYY.pdf
        filename = f"{safe_title}-{timestamp}.pdf"
        
        # 6. Trả về PDF
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
        
        return Response(
            content=pdf_bytes, 
            media_type='application/pdf', 
            headers=headers
        )
    except Exception as e:
        # Phải raise HTTPException để FastAPI xử lý
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo PDF: {str(e)}")
    finally:
        cur.close()
        conn.close() # <-- Luôn đóng kết nối