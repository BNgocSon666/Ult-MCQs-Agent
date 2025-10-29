import React, { useState } from 'react';
import api from '../services/api';

// Chúng ta sẽ tạo file CSS này ở bước 2
import './AgentUploader.css'; 

// Component này sẽ được tạo ở bước 4
import ReviewModal from './ReviewModal'; 

function AgentUploader() {
  const [file, setFile] = useState(null);
  const [numQuestions, setNumQuestions] = useState(5);
  const [summaryMode, setSummaryMode] = useState('auto');
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  // State để lưu kết quả từ API và mở Modal
  const [apiResult, setApiResult] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Vui lòng chọn một file.');
      return;
    }

    setError('');
    setIsLoading(true);
    setApiResult(null);

    // Tạo FormData để gửi file
    const formData = new FormData();
    formData.append('file', file);
    formData.append('num_questions', numQuestions);
    formData.append('summary_mode', summaryMode);

    // Xác định endpoint dựa trên loại file
    const fileType = file.type;
    let endpoint = '/agent/text'; // Mặc định
    if (fileType.startsWith('audio/')) {
      endpoint = '/agent/audio';
    }

    try {
      // Gọi API (đã tự động đính kèm token)
      const response = await api.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      // Lưu kết quả vào state, việc này sẽ kích hoạt Modal
      setApiResult(response.data); 

    } catch (err) {
      if (err.response && err.response.data) {
        setError(err.response.data.detail || 'Lỗi xử lý file.');
      } else {
        setError('Lỗi kết nối máy chủ.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="uploader-container">
      <h3>Tạo câu hỏi từ tài liệu</h3>
      <p>Tải lên file (PDF, DOCX, TXT, MP3, WAV) để AI tự động phân tích và tạo bộ câu hỏi trắc nghiệm.</p>
      
      <form onSubmit={handleSubmit} className="uploader-form">
        <div className="form-group">
          <label htmlFor="file-upload">Chọn file:</label>
          <input 
            id="file-upload"
            type="file" 
            accept=".pdf,.docx,.txt,.mp3,.wav,.m4a"
            onChange={handleFileChange} 
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="num-questions">Số câu hỏi (tối đa):</label>
            <input 
              id="num-questions"
              type="number" 
              value={numQuestions}
              onChange={(e) => setNumQuestions(e.target.value)}
              min="1"
              max="20"
            />
          </div>

          <div className="form-group">
            <label htmlFor="summary-mode">Chế độ tóm tắt:</label>
            <select 
              id="summary-mode"
              value={summaryMode}
              onChange={(e) => setSummaryMode(e.target.value)}
            >
              <option value="auto">Tự động (Nếu dài)</option>
              <option value="force">Luôn luôn</option>
              <option value="none">Không bao giờ</option>
            </select>
          </div>
        </div>
        
        {/* Nút bấm có trạng thái loading */}
        <button type="submit" className="upload-button" disabled={isLoading}>
          {isLoading ? 'Đang xử lý...' : 'Bắt đầu tạo'}
        </button>

        {error && <p className="error-message">{error}</p>}
      </form>

      {/* Khi apiResult có dữ liệu, Modal này sẽ tự động hiển thị.
        Chúng ta truyền hàm setApiResult để Modal có thể tự đóng (bằng cách set lại là null)
      */}
      {apiResult && (
        <ReviewModal 
          result={apiResult} 
          onClose={() => setApiResult(null)} 
        />
      )}
    </div>
  );
}

export default AgentUploader;