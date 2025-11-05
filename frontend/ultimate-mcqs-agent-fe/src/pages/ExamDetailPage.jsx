import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import './ExamDetailPage.css'; // Sẽ tạo ở bước 4

// Component con để hiển thị câu hỏi (chỉ xem)
function QuestionView({ question, index }) {
  const [options, setOptions] = useState([]);
  
  useEffect(() => {
    try {
      setOptions(JSON.parse(question.options || '[]'));
    } catch (e) { setOptions([]); }
  }, [question.options]);

  const getQuestionText = () => {
    try {
      return JSON.parse(question.question_text);
    } catch (e) {
      return question.question_text;
    }
  };

  return (
    <div className="question-view-item">
      <strong>Câu {index + 1}:</strong> {getQuestionText()}
      <ul className="question-view-options">
        {options.map((opt, i) => {
          const letter = String.fromCharCode(65 + i);
          return (
            <li 
              key={i} 
              className={letter === question.answer_letter ? 'correct' : ''}
            >
              {opt}
            </li>
          );
        })}
      </ul>
    </div>
  );
}


// Component Trang chính
function ExamDetailPage() {
  const [exam, setExam] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  
  // useParams lấy :exam_id từ URL
  const { exam_id } = useParams(); 
  const navigate = useNavigate();

  // 1. Tải chi tiết đề thi khi trang mở ra
  useEffect(() => {
    const fetchExamDetail = async () => {
      setIsLoading(true);
      try {
        const response = await api.get(`/exams/${exam_id}`);
        setExam(response.data);
      } catch (err) {
        setError('Không thể tải chi tiết đề thi.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchExamDetail();
  }, [exam_id]); // Chạy lại nếu exam_id thay đổi

  // 2. Hàm xử lý copy link
  const handleCopyLink = () => {
    // Tạo link chia sẻ (ví dụ: http://localhost:5173/take/...)
    // Chúng ta sẽ định nghĩa route /take/... ở Giai đoạn 4
    const shareLink = `${window.location.origin}/take/${exam.share_token}`;
    navigator.clipboard.writeText(shareLink);
    alert('Đã sao chép link làm bài!');
  };

  if (isLoading) return <div className="loading-container">Đang tải chi tiết...</div>;
  if (error) return <div className="error-container">{error}</div>;
  if (!exam) return <div className="loading-container">Không tìm thấy đề thi.</div>;

  // Lấy link PDF (Backend của bạn đã có /export-pdf)
  // Lưu ý: api.defaults.baseURL là 'http://127.0.0.1:8000'
  const pdfUrl = `${api.defaults.baseURL}/exams/${exam.exam_id}/export-pdf`;

  return (
    <div className="exam-detail-page">
      
      {/* --- Cột 1: Thông tin và Hành động --- */}
      <div className="exam-detail-sidebar">
        <button onClick={() => navigate(-1)} className="back-button">
          &larr; Quay lại danh sách
        </button>
        
        <div className="detail-card info-card">
          <h2>{exam.title}</h2>
          <p>{exam.description || 'Không có mô tả.'}</p>
        </div>

        <div className="detail-card actions-card">
          <h3>Chia sẻ</h3>
          <p>Gửi link này cho người khác để họ làm bài.</p>
          <input 
            type="text" 
            readOnly 
            value={`${window.location.origin}/take/${exam.share_token}`}
            className="share-link-input"
          />
          <button onClick={handleCopyLink} className="action-button copy">
            Sao chép link
          </button>
        </div>

        <div className="detail-card actions-card">
          <h3>Xuất file</h3>
          <p>Lưu một bản PDF của đề thi (bao gồm đáp án).</p>
          {/* Nút này là một thẻ <a> để tải file, nhưng nó cần token.
              Vì thẻ <a> không tự gửi header, chúng ta cần 1 cách khác 
              (Hoặc là mở link ở tab mới, yêu cầu user đăng nhập bên đó)
          */}
          <a 
            href={pdfUrl} 
            target="_blank" 
            rel="noopener noreferrer"
            className="action-button pdf"
            // Tạm thời, cách này yêu cầu user phải đăng nhập
            // vào 127.0.0.1:8000 trên trình duyệt
            // Cách tốt hơn (phức tạp) là fetch() và tạo blob URL
            onClick={() => alert('Một tab mới sẽ mở ra để tải PDF. Bạn có thể cần đăng nhập ở tab đó nếu token hết hạn.')}
          >
            Xuất ra PDF
          </a>
        </div>
      </div>

      {/* --- Cột 2: Danh sách câu hỏi --- */}
      <div className="exam-detail-main">
        <h3>Nội dung đề thi ({exam.questions.length} câu)</h3>
        <div className="questions-list-view">
          {exam.questions.map((q, index) => (
            <QuestionView 
              key={q.question_id}
              question={q}
              index={index}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default ExamDetailPage;