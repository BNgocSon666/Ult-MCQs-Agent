import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './MyQuestionsPage.css'; // Sẽ tạo ở bước 4
import { useAuth } from '../context/AuthContext'; // Để lấy user ID

// Component Card câu hỏi (con)
function QuestionCard({ question, onDelete }) {
  const [options, setOptions] = useState([]);
  
  // Dữ liệu 'options' và 'question_text' trong DB của bạn là JSON string
  useEffect(() => {
    try {
      setOptions(JSON.parse(question.options || '[]'));
    } catch (e) {
      setOptions(['Lỗi parse options']);
    }
  }, [question.options]);

  const handleDelete = () => {
    if (window.confirm('Bạn có chắc muốn xóa câu hỏi này?')) {
      onDelete(question.question_id);
    }
  };

  return (
    <div className="my-question-card">
      <div className="card-q-text">
        {/* Thử parse question_text, vì nó cũng có thể là JSON string */}
        {(() => {
          try {
            return JSON.parse(question.question_text);
          } catch (e) {
            return question.question_text;
          }
        })()}
      </div>
      <ul className="card-q-options">
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
      <div className="card-q-footer">
        <span className={`q-status status-${question.status_by_agent}`}>
          AI: {question.total_score || 0}đ ({question.status_by_agent})
        </span>
        <div className="card-q-actions">
          <button className="q-action-btn edit">Sửa</button>
          <button className="q-action-btn delete" onClick={handleDelete}>Xóa</button>
        </div>
      </div>
    </div>
  );
}


// Component Trang chính (cha)
function MyQuestionsPage() {
  const [questions, setQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth(); // Lấy thông tin user

  // Hàm gọi API để lấy danh sách câu hỏi
  const fetchQuestions = async () => {
    setIsLoading(true);
    try {
      // API này đã được bảo vệ bằng token (nhờ axios interceptor)
      const response = await api.get('/questions'); 
      setQuestions(response.data.questions || []);
    } catch (err) {
      setError('Không thể tải thư viện câu hỏi.');
    } finally {
      setIsLoading(false);
    }
  };

  // Gọi API khi component được tải
  useEffect(() => {
    if (user) { // Chỉ gọi khi đã có thông tin user
      fetchQuestions();
    }
  }, [user]); // Phụ thuộc vào 'user'

  // Hàm xử lý xóa câu hỏi
  const handleDeleteQuestion = async (questionId) => {
    try {
      await api.delete(`/questions/${questionId}`);
      // Tải lại danh sách câu hỏi sau khi xóa thành công
      fetchQuestions(); 
    } catch (err) {
      alert('Lỗi: Không thể xóa câu hỏi.');
    }
  };

  if (isLoading) return <div className="loading-container">Đang tải...</div>;
  if (error) return <div className="error-container">{error}</div>;

  return (
    <div className="my-questions-page">
      <div className="page-header">
        <h2>Thư viện câu hỏi của tôi</h2>
        <p>Tổng cộng: {questions.length} câu hỏi</p>
      </div>
      
      <div className="questions-list-container">
        {questions.length === 0 ? (
          <p>Bạn chưa lưu câu hỏi nào. Hãy qua tab "Tạo mới (AI)"!</p>
        ) : (
          questions.map(q => (
            <QuestionCard 
              key={q.question_id} 
              question={q} 
              onDelete={handleDeleteQuestion} 
            />
          ))
        )}
      </div>
    </div>
  );
}

export default MyQuestionsPage;