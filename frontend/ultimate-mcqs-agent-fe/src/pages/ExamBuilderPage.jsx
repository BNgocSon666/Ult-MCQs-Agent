import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './ExamBuilderPage.css'; // Sẽ tạo ở bước 4

// Component con để hiển thị 1 câu hỏi trong danh sách
function QuestionSelectItem({ question, onSelect, isSelected }) {
  const [options, setOptions] = useState([]);

  useEffect(() => {
    // Parse 'options' và 'question_text' vì chúng là JSON string
    try {
      setOptions(JSON.parse(question.options || '[]'));
    } catch (e) {
      setOptions([]);
    }
  }, [question.options]);

  const getQuestionText = () => {
    try {
      return JSON.parse(question.question_text);
    } catch (e) {
      return question.question_text;
    }
  };

  return (
    <div 
      className={`question-select-item ${isSelected ? 'selected' : ''}`}
      onClick={() => onSelect(question.question_id)}
    >
      <input 
        type="checkbox" 
        checked={isSelected} 
        onChange={() => onSelect(question.question_id)} 
        className="question-checkbox"
      />
      <div className="question-select-content">
        <div className="question-select-text">{getQuestionText()}</div>
        <div className="question-select-answer">
          Đáp án: {question.answer_letter}
        </div>
      </div>
    </div>
  );
}


// Component Trang chính
function ExamBuilderPage() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [allQuestions, setAllQuestions] = useState([]);
  
  // Dùng một object (map) để lưu các ID đã chọn cho nhanh
  // ví dụ: { 15: true, 22: true }
  const [selectedIds, setSelectedIds] = useState({});
  
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  // 1. Tải thư viện câu hỏi khi trang mở ra
  useEffect(() => {
    const fetchQuestions = async () => {
      setIsLoading(true);
      try {
        const response = await api.get('/questions');
        setAllQuestions(response.data.questions || []);
      } catch (err) {
        setError('Không thể tải thư viện câu hỏi.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchQuestions();
  }, []);

  // 2. Hàm xử lý khi check/uncheck một câu hỏi
  const handleSelectQuestion = (questionId) => {
    setSelectedIds(prevIds => {
      const newIds = { ...prevIds };
      if (newIds[questionId]) {
        delete newIds[questionId]; // Bỏ chọn
      } else {
        newIds[questionId] = true; // Thêm vào
      }
      return newIds;
    });
  };

  // 3. Hàm xử lý khi bấm nút "Lưu đề thi"
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('Tiêu đề không được để trống.');
      return;
    }
    
    // Lấy danh sách các ID đã chọn
    const idsArray = Object.keys(selectedIds).filter(id => selectedIds[id]);
    
    if (idsArray.length === 0) {
      setError('Bạn phải chọn ít nhất một câu hỏi.');
      return;
    }

    // Chuyển mảng [15, 22] thành string "15,22"
    const questionIdsString = idsArray.join(',');

    setIsSaving(true);
    setError('');

    try {
      // Backend của bạn (exams_router.py) đang nhận Form
      const formData = new URLSearchParams();
      formData.append('title', title);
      formData.append('description', description);
      formData.append('question_ids', questionIdsString);

      await api.post('/exams', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      // Tạo thành công, quay về trang danh sách
      navigate('/dashboard/exams');

    } catch (err) {
      setError('Lỗi khi lưu đề thi. Vui lòng thử lại.');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) return <div className="loading-container">Đang tải thư viện...</div>;

  return (
    <div className="exam-builder-page">
      <form onSubmit={handleSubmit} className="exam-builder-form">
        <h2>Tạo đề thi mới</h2>
        
        {/* --- Phần 1: Thông tin chung --- */}
        <div className="form-section">
          <div className="form-group">
            <label htmlFor="exam-title">Tiêu đề đề thi</label>
            <input 
              id="exam-title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ví dụ: Đề kiểm tra giữa kỳ..."
            />
          </div>
          <div className="form-group">
            <label htmlFor="exam-description">Mô tả (Không bắt buộc)</label>
            <textarea
              id="exam-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Ví dụ: Đề thi này bao gồm 3 chương đầu..."
            />
          </div>
        </div>

        {/* --- Phần 2: Chọn câu hỏi --- */}
        <div className="form-section">
          <h3>Chọn câu hỏi từ thư viện</h3>
          <div className="question-picker-list">
            {allQuestions.length === 0 ? (
              <p>Thư viện của bạn chưa có câu hỏi nào.</p>
            ) : (
              allQuestions.map(q => (
                <QuestionSelectItem 
                  key={q.question_id}
                  question={q}
                  isSelected={!!selectedIds[q.question_id]}
                  onSelect={handleSelectQuestion}
                />
              ))
            )}
          </div>
        </div>
        
        {error && <p className="error-message">{error}</p>}

        {/* --- Phần 3: Nút bấm --- */}
        <div className="form-actions">
          <button 
            type="button" 
            className="builder-button cancel" 
            onClick={() => navigate('/dashboard/exams')}
          >
            Hủy
          </button>
          <button 
            type="submit" 
            className="builder-button save"
            disabled={isSaving}
          >
            {isSaving ? 'Đang lưu...' : 'Lưu đề thi'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ExamBuilderPage;