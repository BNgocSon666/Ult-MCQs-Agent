import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import './ExamStartPage.css'; // Sẽ tạo ở bước 2

function ExamStartPage() {
  const [exam, setExam] = useState(null); // Thông tin đề thi
  const [guestName, setGuestName] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState('');
  
  const { share_token } = useParams(); // Lấy token từ URL
  const { user, isAuthenticated } = useAuth(); // Kiểm tra xem user đã login chưa
  const navigate = useNavigate();

  // 1. Tải thông tin đề thi bằng share_token
  useEffect(() => {
    const fetchExamInfo = async () => {
      setIsLoading(true);
      setError('');
      try {
        const response = await api.get(`/exams/token/${share_token}`);
        setExam(response.data); // Lưu thông tin (exam_id, title, desc)
      } catch (err) {
        setError('Không tìm thấy đề thi này hoặc link đã hết hạn.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchExamInfo();
  }, [share_token]);

  // 2. Xử lý khi bấm nút "Bắt đầu"
  const handleStartSession = async (e) => {
    e.preventDefault();
    
    // Nếu là khách, phải nhập tên
    if (!isAuthenticated && !guestName.trim()) {
      setError('Vui lòng nhập tên của bạn để bắt đầu.');
      return;
    }

    setIsStarting(true);
    setError('');

    try {
      const formData = new URLSearchParams();
      
      // Backend (sessions_router) chờ 'guest_name' nếu là khách
      if (!isAuthenticated) {
        formData.append('guest_name', guestName);
      }
      // Nếu đã đăng nhập, AuthContext (api.js) sẽ tự gửi token
      
      // Gọi API /sessions/start/{exam_id}
      const response = await api.post(`/sessions/start/${exam.exam_id}`, formData);
      
      const { session_id } = response.data;
      
      // Chuyển hướng sang trang làm bài (sẽ tạo ở bước sau)
      navigate(`/session/${session_id}`);

    } catch (err) {
      setError('Lỗi khi bắt đầu phiên làm bài. Vui lòng thử lại.');
    } finally {
      setIsStarting(false);
    }
  };

  // Các trạng thái chờ tải...
  if (isLoading) return <div className="start-page-container"><div className="loading-box">Đang tải đề thi...</div></div>;
  if (error) return <div className="start-page-container"><div className="loading-box error">{error}</div></div>;

  return (
    <div className="start-page-container">
      <div className="start-exam-card">
        <h2>{exam.title}</h2>
        <p>{exam.description || 'Sẵn sàng để bắt đầu bài kiểm tra.'}</p>
        
        <form onSubmit={handleStartSession}>
          {/* Nếu đã đăng nhập: Hiển thị lời chào
            Nếu là khách: Hiển thị ô nhập tên
          */}
          {isAuthenticated ? (
            <div className="welcome-user">
              Bạn sẽ làm bài với tư cách: <strong>{user.username}</strong>
            </div>
          ) : (
            <div className="form-group">
              <label htmlFor="guest-name">Nhập tên của bạn:</label>
              <input
                id="guest-name"
                type="text"
                value={guestName}
                onChange={(e) => setGuestName(e.target.value)}
                placeholder="Ví dụ: Nguyễn Văn A"
                required
              />
            </div>
          )}

          <button type="submit" className="start-button" disabled={isStarting}>
            {isStarting ? 'Đang tải...' : 'Bắt đầu làm bài'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default ExamStartPage;