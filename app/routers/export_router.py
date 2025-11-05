import datetime
from typing import List
from fastapi import APIRouter, Response
from pydantic import BaseModel, Field
from weasyprint import HTML

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
    questions: List[MCQItem] = Field(description="Danh sách các câu hỏi trắc nghiệm")

# ---- 2. Hàm helper để chuyển MCQs thành HTML/CSS ----

def format_mcqs_to_html(questions: List[MCQItem]) -> str:
    """
    Hàm này nhận dữ liệu tóm tắt và MCQs và biến nó thành một chuỗi HTML.
    (Đã cập nhật: Tách riêng CSS h1, căn giữa và bỏ gạch chân h1)
    """
    
    # CSS để PDF trông đẹp hơn
    css_style = """
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 12px;
            line-height: 1.6;
            color: #333;
        }

        /* --- ĐÃ SỬA CSS Ở ĐÂY --- */

        /* Tiêu đề chính H1: Căn giữa, bỏ gạch chân */
        h1 { 
            font-size: 24px; 
            text-align: center; /* Căn giữa */
            color: #000;
            padding-bottom: 5px;
            margin-bottom: 25px; /* Thêm khoảng cách dưới */
            border-bottom: none; /* Bỏ gạch chân */
            page-break-after: avoid;
        }

        /* Tiêu đề phụ H2 (Nếu sau này dùng) */
        h2 { 
            font-size: 18px; 
            color: #000;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 5px;
            page-break-after: avoid;
        }
        
        /* --- KẾT THÚC SỬA CSS --- */

        .summary {
            background-color: #f9f9f9;
            border-left: 4px solid #007bff;
            padding: 10px 15px;
            margin-bottom: 20px;
            page-break-inside: avoid;
        }
        .question-block {
            margin-bottom: 25px;
            padding-top: 10px;
            page-break-inside: avoid; /* Tránh ngắt trang giữa câu hỏi */
        }
        .question {
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 8px;
        }
        .options {
            list-style-type: none;
            padding-left: 15px;
        }
        .options li {
            margin-bottom: 5px;
        }
        .correct-answer {
            font-weight: bold;
            color: #28a745; /* Màu xanh lá cho đáp án đúng */
        }
    </style>
    """
    
    # Bắt đầu xây dựng HTML
    html_content = f"<html><head><meta charset='UTF-8'>{css_style}</head><body>"
    html_content += "<h1>Báo cáo Câu hỏi Trắc nghiệm</h1>"
    
    # (Phần tóm tắt và tiêu đề 2 đã được xóa ở lần trước)
    
    # Vòng lặp (giữ nguyên)
    for i, q in enumerate(questions): 
        html_content += f"<div class='question-block'>"
        html_content += f"<p class='question'>Câu {i + 1}: {q.question}</p>"
        
        html_content += "<ul class='options'>"

        answer_prefix = q.answer_letter + "." 
        
        for opt in q.options:
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
    summary="Xuất danh sách MCQs và tóm tắt ra file PDF"
)
def export_to_pdf(data: PDFExportRequest):
    """
    Nhận một đối tượng JSON chứa 'summary' và 'mcqs' và trả về một file PDF.
    
    Gửi dữ liệu POST theo cấu trúc của Pydantic model `PDFExportRequest`.
    """
    
    if not data.questions:
        return Response(content="Không có dữ liệu MCQs để xuất.", status_code=400)

    # 1. Định dạng dữ liệu thành HTML
    html_string = format_mcqs_to_html(data.questions)
    
    # 2. Chuyển đổi HTML sang PDF bằng WeasyPrint
    # .write_pdf() trả về một đối tượng bytes
    pdf_bytes = HTML(string=html_string).write_pdf()
    
    # 3. Tạo tên file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"MCQs_Export_{timestamp}.pdf"
    
    # 4. Trả về PDF dưới dạng 'attachment' để trình duyệt tự động tải xuống
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    
    return Response(
        content=pdf_bytes, 
        media_type='application/pdf', 
        headers=headers
    )