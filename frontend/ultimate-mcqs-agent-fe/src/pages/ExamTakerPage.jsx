import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import './ExamTakerPage.css'; // Sẽ tạo ở bước 2

// Component con hiển thị 1 câu hỏi (VÀ NGỮ CẢNH)
function TakerQuestion({ question, index, selectedOption, onSelect }) {
  const [options, setOptions] = useState([]);
  
  // Parse 'options' và 'question_text'
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

  // Lấy ngữ cảnh (nếu có)
  const getContext = () => {
    try {
      return JSON.parse(question.context || '""');
    } catch (e) {
      return question.context;
    }
  };
  
  const context = getContext();

  return (
    <div className="taker-question-card">
      {/* HIỂN THỊ NGỮ CẢNH (Quan trọng) */}
      {context && (
        <div className="question-context">
          <strong>Dựa vào đoạn văn bản sau:</strong>
          <p>"{context}"</p>
        </div>
      )}
      
      <div className="question-text">
        <strong>Câu {index + 1}:</strong> {getQuestionText()}
      </div>
      
      <div className="question-options">
        {options.map((opt, i) => {
          const letter = String.fromCharCode(65 + i); // A, B, C, D
          return (
            <label 
              key={letter} 
              className={`option-label ${selectedOption === letter ? 'selected' : ''}`}
            >
              <input 
                type="radio" 
                name={`question_${question.question_id}`}
                value={letter}
                checked={selectedOption === letter}
                onChange={() => onSelect(question.question_id, letter)}
              />
              {opt}
            </label>
          );
        })}
      </div>
    </div>
  );
}


// Component Trang chính
function ExamTakerPage() {
  const [questions, setQuestions] = useState([]);
  const [examId, setExamId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  
  // State để lưu câu trả lời của user, ví dụ: { 101: 'A', 102: 'C' }
  const [answers, setAnswers] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { session_id } = useParams(); // Lấy session_id từ URL
  const navigate = useNavigate();

  // 1. Tải danh sách câu hỏi
  useEffect(() => {
    const fetchQuestions = async () => {
      setIsLoading(true);
      setError('');
      try {
        const response = await api.get(`/sessions/${session_id}/questions`);
        setQuestions(response.data.questions || []);
        setExamId(response.data.exam_id);
      } catch (err) {
        setError('Không thể tải bài thi. Phiên làm bài có thể đã hết hạn.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchQuestions();
  }, [session_id]);

  // 2. Hàm để cập nhật state 'answers'
  const handleSelectAnswer = (questionId, selectedOption) => {
    setAnswers(prevAnswers => ({
      ...prevAnswers,
      [questionId]: selectedOption
    }));
    // Note: Chúng ta sẽ thêm tự động lưu (auto-save) ở đây sau
  };

  // 3. Hàm nộp bài
  const handleSubmit = async () => {
    if (!window.confirm('Bạn có chắc muốn nộp bài?')) {
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      // BƯỚC A: Lưu các câu trả lời cuối cùng
      const answersToSave = Object.keys(answers).map(qId => ({
        question_id: parseInt(qId),
        selected_option: answers[qId]
      }));
      
      if (answersToSave.length > 0) {
        await api.post(`/sessions/${session_id}/answers`, { answers: answersToSave });
      }

      // BƯỚC B: Chấm điểm
      const response = await api.post(`/sessions/${session_id}/submit`);
      
      // Chuyển hướng đến trang kết quả (sẽ tạo ở bước cuối)
      navigate(`/results/${session_id}`, { state: { score: response.data.total_score } });

    } catch (err) {
      setError('Lỗi khi nộp bài. Vui lòng thử lại.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) return <div className="loading-container">Đang tải bài thi...</div>;
  if (error) return <div className="error-container">{error}</div>;

  return (
    <div className="taker-page-container">
      <div className="taker-header">
        <h1>Đang làm bài...</h1>
        <button 
          className="submit-button" 
          onClick={handleSubmit} 
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Đang nộp...' : 'Nộp bài'}
        </button>
      </div>

      <div className="taker-questions-list">
        {questions.map((q, index) => (
          <TakerQuestion 
            key={q.question_id}
            question={q}
            index={index}
            selectedOption={answers[q.question_id] || null}
            onSelect={handleSelectAnswer}
          />
        ))}
      </div>
      
      {/* Nút nộp bài ở cuối */}
      <div className="taker-footer">
        {error && <p className="error-message">{error}</p>}
        <button 
          className="submit-button" 
          onClick={handleSubmit} 
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Đang nộp...' : 'Nộp bài'}
        </button>
      </div>
    </div>
  );
}

export default ExamTakerPage;