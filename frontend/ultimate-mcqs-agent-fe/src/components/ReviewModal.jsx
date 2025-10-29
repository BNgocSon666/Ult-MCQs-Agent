import React, { useState } from 'react';
import api from '../services/api';

// CSS cho Modal và Card
import './ReviewModal.css';

// Component Card con (Bước 5)
function QuestionReviewCard({ question, index }) {
  const [isExpanded, setIsExpanded] = useState(index === 0); // Mở câu đầu tiên
  const options = question.options || [];
  const answer = question.answer_letter || '?';
  const eval_scores = question._eval_breakdown || {};

  return (
    <div className="question-card">
      <div className="card-header" onClick={() => setIsExpanded(!isExpanded)}>
        <strong>Câu {index + 1}:</strong> {question.question}
        <span className={`score-badge status-${question.status}`}>
          {question.score} điểm
        </span>
      </div>
      
      {isExpanded && (
        <div className="card-content">
          <ul className="options-list">
            {options.map((opt, i) => {
              const letter = String.fromCharCode(65 + i); // A, B, C, D
              return (
                <li key={i} className={letter === answer ? 'correct-answer' : ''}>
                  {opt}
                </li>
              )
            })}
          </ul>
          <div className="eval-details">
            <strong>AI Đánh giá:</strong>
            <ul>
              <li>Accuracy (50): {eval_scores.accuracy || 0}</li>
              <li>Alignment (25): {eval_scores.alignment || 0}</li>
              <li>Distractors (20): {eval_scores.distractors || 0}</li>
              <li>Clarity (5): {eval_scores.clarity || 0}</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}


// Component Modal chính
function ReviewModal({ result, onClose }) {
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  const handleSave = async () => {
    setIsSaving(true);
    setSaveMessage('');
    try {
      // Gọi API /agent/save với toàn bộ payload 'result'
      const response = await api.post('/agent/save', result);
      setSaveMessage(response.data.message || 'Lưu thành công!');
      
      // Tự động đóng sau 2 giây
      setTimeout(() => {
        onClose(); 
      }, 2000);

    } catch (err) {
      setSaveMessage('Lỗi khi lưu. Vui lòng thử lại.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="modal-backdrop"> {/* Lớp mờ che nền */}
      <div className="modal-content">
        
        {/* Header của Modal */}
        <div className="modal-header">
          <h3>Kết quả từ AI</h3>
          <button onClick={onClose} className="close-button">&times;</button>
        </div>
        
        {/* Nội dung của Modal */}
        <div className="modal-body">
          {result.summary && (
            <div className="summary-section">
              <strong>Tóm tắt (nếu có):</strong>
              <p>{result.summary}</p>
            </div>
          )}
          
          <div className="questions-list">
            {result.questions.map((q, index) => (
              <QuestionReviewCard 
                key={index} 
                question={q} 
                index={index} 
              />
            ))}
          </div>
        </div>
        
        {/* Chân của Modal */}
        <div className="modal-footer">
          {saveMessage && <span className="save-message">{saveMessage}</span>}
          <button 
            className="save-button" 
            onClick={handleSave} 
            disabled={isSaving}
          >
            {isSaving ? 'Đang lưu...' : 'Lưu vào thư viện'}
          </button>
        </div>

      </div>
    </div>
  );
}

export default ReviewModal;