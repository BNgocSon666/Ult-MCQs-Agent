import React, { useState } from 'react';
import api from '../services/api';
import './ReviewModal.css'; // Sử dụng chung file CSS

// ===================================================================
// === COMPONENT CON: DÙNG ĐỂ HIỂN THỊ HOẶC SỬA 1 CÂU HỎI ===
// ===================================================================
function QuestionReviewCard({ 
  question, 
  index, 
  onUpdateQuestion // Hàm callback từ cha để cập nhật state
}) {
  const [isEditing, setIsEditing] = useState(false);
  
  // State tạm thời để lưu các thay đổi khi đang edit
  const [editData, setEditData] = useState({
    question: question.question,
    options: [...question.options], // Tạo bản sao
    answer_letter: question.answer_letter
  });

  const eval_scores = question._eval_breakdown || {};

  // Hàm xử lý khi gõ vào ô câu hỏi
  const handleQuestionTextChange = (e) => {
    setEditData({ ...editData, question: e.target.value });
  };

  // Hàm xử lý khi gõ vào ô lựa chọn (option)
  const handleOptionChange = (optIndex, newValue) => {
    const newOptions = [...editData.options];
    newOptions[optIndex] = newValue;
    setEditData({ ...editData, options: newOptions });
  };

  // Hàm xử lý khi chọn lại đáp án đúng
  const handleAnswerChange = (e) => {
    setEditData({ ...editData, answer_letter: e.target.value });
  };

  // Hủy bỏ chỉnh sửa
  const handleCancel = () => {
    // Reset lại state edit về giá trị gốc
    setEditData({
      question: question.question,
      options: [...question.options],
      answer_letter: question.answer_letter
    });
    setIsEditing(false);
  };

  // Lưu chỉnh sửa
  const handleSaveEdit = () => {
    // Tạo object câu hỏi mới đã được cập nhật
    const updatedQuestion = {
      ...question, // Giữ lại các trường cũ (như _eval_breakdown, score...)
      ...editData  // Ghi đè các trường đã sửa (question, options, answer_letter)
    };
    
    // Gọi hàm của cha (ReviewModal) để cập nhật state tổng
    onUpdateQuestion(index, updatedQuestion);
    setIsEditing(false); // Tắt chế độ chỉnh sửa
  };


  // === Giao diện khi ở chế độ CHỈNH SỬA ===
  if (isEditing) {
    return (
      <div className="question-card editing">
        <div className="card-content-edit">
          {/* 1. Sửa câu hỏi */}
          <label>Nội dung câu hỏi:</label>
          <textarea
            className="edit-textarea"
            value={editData.question}
            onChange={handleQuestionTextChange}
          />
          
          {/* 2. Sửa các lựa chọn */}
          <label>Các lựa chọn:</label>
          <div className="edit-options-grid">
            {editData.options.map((opt, i) => {
              const letter = String.fromCharCode(65 + i); // A, B, C, D
              return (
                <div key={i} className="edit-option-item">
                  <input
                    type="radio"
                    name={`answer_edit_${index}`}
                    value={letter}
                    checked={editData.answer_letter === letter}
                    onChange={handleAnswerChange}
                  />
                  <input
                    type="text"
                    className="edit-input"
                    value={opt}
                    onChange={(e) => handleOptionChange(i, e.target.value)}
                  />
                </div>
              );
            })}
          </div>
        </div>

        {/* 3. Nút bấm lưu/hủy */}
        <div className="card-edit-actions">
          <button onClick={handleCancel} className="edit-button cancel">Hủy</button>
          <button onClick={handleSaveEdit} className="edit-button save">Lưu</button>
        </div>
      </div>
    );
  }

  // === Giao diện khi ở chế độ XEM (Mặc định) ===
  return (
    <div className="question-card">
      <div className="card-header" onClick={() => setIsEditing(true)}> {/* Click để sửa */}
        <strong>Câu {index + 1}:</strong> {question.question}
        <span className={`score-badge status-${question.status}`}>
          {question.score} điểm
        </span>
      </div>
      
      {/* Nút sửa (thêm mới) */}
      <button onClick={() => setIsEditing(true)} className="edit-button-simple">
        Chỉnh sửa
      </button>

      <div className="card-content">
        <ul className="options-list">
          {question.options.map((opt, i) => {
            const letter = String.fromCharCode(65 + i);
            return (
              <li key={i} className={letter === question.answer_letter ? 'correct-answer' : ''}>
                {opt}
              </li>
            );
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
    </div>
  );
}


// ===================================================================
// === COMPONENT MODAL CHÍNH (ĐÃ CẬP NHẬT) ===
// ===================================================================
function ReviewModal({ result, onClose }) {
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');
  
  // *** NÂNG CẤP QUAN TRỌNG ***
  // 1. Sao chép 'result.questions' vào state của component
  const [editableQuestions, setEditableQuestions] = useState(result.questions);

  // 2. Hàm để component con (Card) gọi để cập nhật state này
  const handleUpdateQuestion = (indexToUpdate, updatedQuestion) => {
    const newQuestions = editableQuestions.map((q, index) => {
      if (index === indexToUpdate) {
        return updatedQuestion;
      }
      return q;
    });
    setEditableQuestions(newQuestions);
  };

  // 3. Hàm 'handleSave' giờ sẽ gửi 'editableQuestions' đi
  const handleSave = async () => {
    setIsSaving(true);
    setSaveMessage('');
    
    // Tạo payload mới với các câu hỏi đã được chỉnh sửa
    const payloadToSave = {
      ...result, // Giữ lại summary, filename, raw_text, mode...
      questions: editableQuestions // Chỉ thay thế 'questions' bằng bản đã sửa
    };

    try {
      const response = await api.post('/agent/save', payloadToSave);
      setSaveMessage(response.data.message || 'Lưu thành công!');
      
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
    <div className="modal-backdrop">
      <div className="modal-content">
        
        <div className="modal-header">
          <h3>Kết quả từ AI</h3>
          <button onClick={onClose} className="close-button">&times;</button>
        </div>
        
        <div className="modal-body">
          {result.summary && (
            <div className="summary-section">
              <strong>Tóm tắt (nếu có):</strong>
              <p>{result.summary}</p>
            </div>
          )}
          
          <div className="source-notification">
            {/* ... (code thông báo nguồn gốc, giữ nguyên) ... */}
            {result.mode === 'summary+mcqs' && (
              <span>Các câu hỏi dưới đây được tạo dựa trên <strong>bản tóm tắt</strong>.</span>
            )}
            {result.mode === 'mcqs' && (
              <span>Các câu hỏi dưới đây được tạo dựa trên <strong>nội dung đầy đủ</strong> của tài liệu.</span>
            )}
            {!result.mode && (
              <span>Nguồn gốc câu hỏi: Không rõ.</span>
            )}
          </div>

          <div className="questions-list">
            {/* 4. Truyền 'editableQuestions' và 'handleUpdateQuestion' xuống con */}
            {editableQuestions.map((q, index) => (
              <QuestionReviewCard 
                key={index} // Quan trọng: React cần key để nhận diện
                question={q} 
                index={index} 
                onUpdateQuestion={handleUpdateQuestion} // Truyền hàm update
              />
            ))}
          </div>
        </div>
        
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