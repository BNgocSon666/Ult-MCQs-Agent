import React, { useState } from 'react';
import './HowToPage.css'; // Chúng ta sẽ tạo file CSS ở bước 2

// Dữ liệu cho các mục hướng dẫn
// Dựa trên các file: AgentUploader.jsx, ReviewModal.jsx, ExamBuilderPage.jsx, ExamDetailPage.jsx, ExamTakerPage.jsx
const guideData = [
  {
    question: '1. Làm thế nào để tạo câu hỏi bằng AI?',
    answer: [
      "Đây là luồng nghiệp vụ chính của hệ thống.",
      "<strong>Bước 1:</strong> Đi đến mục <strong>'Tạo mới (AI)'</strong> trên thanh điều hướng.",
      "<strong>Bước 2:</strong> Nhấn 'Chọn file' và tải lên tài liệu của bạn (PDF, DOCX, TXT, hoặc file âm thanh MP3, WAV...).",
      "<strong>Bước 3:</strong> Chọn 'Số câu hỏi' bạn muốn và 'Chế độ tóm tắt' (nên để 'Tự động').",
      "<strong>Bước 4:</strong> Nhấn nút 'Bắt đầu tạo' và chờ AI xử lý (có thể mất 1-2 phút).",
      "<strong>Bước 5:</strong> Một cửa sổ 'Kết quả từ AI' (Review Modal) sẽ hiện lên.",
      "<strong>Bước 6 (Quan trọng):</strong> Tại đây, bạn có thể xem lại, nhấn 'Chỉnh sửa' để sửa lại câu hỏi, đáp án... cho đến khi hài lòng.",
      "<strong>Bước 7:</strong> Nhấn nút 'Lưu vào thư viện' để lưu các câu hỏi này vào tài khoản của bạn."
    ]
  },
  {
    question: '2. Làm thế nào để tạo một Đề thi?',
    answer: [
      "Bạn chỉ có thể tạo đề thi từ các câu hỏi đã có trong 'Thư viện câu hỏi'.",
      "<strong>Bước 1:</strong> Đảm bảo bạn đã tạo câu hỏi bằng AI (xem Mục 1) và chúng đã được lưu.",
      "<strong>Bước 2:</strong> Đi đến mục <strong>'Đề thi của tôi'</strong> trên thanh điều hướng.",
      "<strong>Bước 3:</strong> Nhấn nút '+ Tạo đề thi mới'.",
      "<strong>Bước 4:</strong> Bạn sẽ được chuyển đến trang 'Tạo đề thi mới'.",
      "<strong>Bước 5:</strong> Nhập 'Tiêu đề đề thi' và 'Mô tả'.",
      "<strong>Bước 6:</strong> Ở phần 'Chọn câu hỏi từ thư viện', nhấp chuột để **chọn (tick)** những câu hỏi bạn muốn thêm vào đề thi này.",
      "<strong>Bước 7:</strong> Nhấn nút 'Lưu đề thi' để hoàn tất."
    ]
  },
  {
    question: '3. Làm thế nào để chia sẻ và làm bài thi?',
    answer: [
      "Luồng này có 2 phần: cho người tạo đề và người làm bài.",
      "<strong>Phần 1: Dành cho Người tạo đề:</strong>",
      "<strong>Bước 1:</strong> Đi đến <strong>'Đề thi của tôi'</strong> và nhấp vào tiêu đề của đề thi bạn muốn chia sẻ.",
      "<strong>Bước 2:</strong> Bạn sẽ ở trang 'Chi tiết Đề thi'.",
      "<strong>Bước 3:</strong> Trong thẻ 'Chia sẻ', nhấn nút 'Sao chép link'.",
      "<strong>Bước 4:</strong> Gửi link này (ví dụ: /take/abc123xyz) cho người làm bài.",
      "<strong>Bước 5:</strong> Bạn có thể nhấn 'Xem kết quả' để xem thống kê ai đã làm bài và điểm số của họ.",
      "<br/>",
      "<strong>Phần 2: Dành cho Người làm bài:</strong>",
      "<strong>Bước 1:</strong> Mở link mà giáo viên đã gửi.",
      "<strong>Bước 2:</strong> Bạn sẽ thấy trang 'Bắt đầu làm bài'.",
      "<strong>Bước 3:</strong> Nếu bạn chưa đăng nhập, hãy nhập tên của bạn vào ô và nhấn 'Bắt đầu'.",
      "<strong>Bước 4:</strong> Trả lời các câu hỏi trong trang làm bài.",
      "<strong>Bước 5:</strong> Nhấn nút 'Nộp bài' khi hoàn tất.",
      "<strong>Bước 6:</strong> Hệ thống sẽ tự động chấm điểm và đưa bạn đến trang 'Kết quả' để xem chi tiết câu đúng/sai."
    ]
  },
  {
    question: '4. Làm thế nào để quản lý tài khoản?',
    answer: [
      "<strong>Bước 1:</strong> Nhấn vào nút <strong>'Tài khoản'</strong> trên góc phải màn hình.",
      "<strong>Bước 2:</strong> Bạn sẽ được chuyển đến trang 'Profile'.",
      "<strong>Bước 3 (Đổi thông tin):</strong> Để đổi Tên, Email, SĐT, hãy nhấn nút 'Chỉnh sửa thông tin', thay đổi và nhấn 'Lưu'.",
      "<strong>Bước 4 (Đổi mật khẩu):</strong> Để đổi mật khẩu, hãy sử dụng biểu mẫu 'Bảo mật & Đăng nhập' ở phía dưới. Bạn cần nhập mật khẩu cũ và mật khẩu mới."
    ]
  }
];

// Component con cho từng mục Accordion
function AccordionItem({ item, isOpen, onClick }) {
  return (
    <div className="accordion-item">
      <div className="accordion-header" onClick={onClick}>
        <span>{item.question}</span>
        <span className="accordion-toggle">{isOpen ? '−' : '+'}</span>
      </div>
      {isOpen && (
        <div className="accordion-content">
          {item.answer.map((line, index) => (
            <p key={index} dangerouslySetInnerHTML={{ __html: line }} />
          ))}
        </div>
      )}
    </div>
  );
}

// Component trang chính
function HowToPage() {
  const [openIndex, setOpenIndex] = useState(0); // Mở mục đầu tiên

  const handleItemClick = (index) => {
    setOpenIndex(openIndex === index ? null : index); // Đóng/mở
  };

  return (
    <div className="how-to-page">
      <div className="how-to-header">
        <h2>Hướng dẫn sử dụng</h2>
        <p>Tìm hiểu các bước cơ bản để sử dụng Ultimate MCQs Agent hiệu quả.</p>
      </div>
      <div className="accordion-container">
        {guideData.map((item, index) => (
          <AccordionItem
            key={index}
            item={item}
            isOpen={openIndex === index}
            onClick={() => handleItemClick(index)}
          />
        ))}
      </div>
    </div>
  );
}

export default HowToPage;