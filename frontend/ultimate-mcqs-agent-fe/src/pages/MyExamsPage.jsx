import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './MyExamsPage.css'; // Sẽ tạo ở bước 2
import { useAuth } from '../context/AuthContext';

// Component Card hiển thị một đề thi
function ExamCard({ exam, onDelete }) {
  const navigate = useNavigate();

  const handleDelete = (e) => {
    e.stopPropagation(); // Ngăn việc click vào nút xóa bị tính là click vào card
    if (window.confirm(`Bạn có chắc muốn xóa đề thi: "${exam.title}"?`)) {
      onDelete(exam.exam_id);
    }
  };

  const handleNavigate = () => {
    // Chuyển hướng đến trang chi tiết (chúng ta sẽ làm sau)
    // navigate(`/dashboard/exams/${exam.exam_id}`);
    navigate(`/dashboard/exams/${exam.exam_id}`);
  };

  // Định dạng lại ngày tháng
  const formattedDate = new Date(exam.created_at).toLocaleDateString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });

  return (
    <div className="exam-card" onClick={handleNavigate}>
      <div className="card-body">
        <h3 className="exam-title">{exam.title}</h3>
        <p className="exam-description">{exam.description || 'Không có mô tả'}</p>
      </div>
      <div className="card-footer">
        <span className="exam-date">Ngày tạo: {formattedDate}</span>
        <button className="exam-delete-btn" onClick={handleDelete}>
          Xóa
        </button>
      </div>
    </div>
  );
}

// Component Trang chính
function MyExamsPage() {
  const [exams, setExams] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();
  const navigate = useNavigate();

  // Hàm gọi API để lấy danh sách đề thi
  const fetchExams = async () => {
    setIsLoading(true);
    try {
      const response = await api.get('/exams');
      setExams(response.data.exams || []);
    } catch (err) {
      setError('Không thể tải danh sách đề thi.');
    } finally {
      setIsLoading(false);
    }
  };

  // Gọi API khi component được tải
  useEffect(() => {
    if (user) {
      fetchExams();
    }
  }, [user]);

  // Hàm xử lý xóa đề thi
  const handleDeleteExam = async (examId) => {
    try {
      await api.delete(`/exams/${examId}`);
      fetchExams(); // Tải lại danh sách sau khi xóa
    } catch (err) {
      alert('Lỗi: Không thể xóa đề thi.');
    }
  };

  if (isLoading) return <div className="loading-container">Đang tải...</div>;
  if (error) return <div className="error-container">{error}</div>;

  return (
    <div className="my-exams-page">
      <div className="page-header">
        <h2>Đề thi của tôi</h2>
        <button 
          className="create-exam-btn" 
          onClick={() => navigate('/dashboard/exams/new')}
        >
          + Tạo đề thi mới
        </button>
      </div>

      <div className="exams-list-container">
        {exams.length === 0 ? (
          <p>Bạn chưa tạo đề thi nào.</p>
        ) : (
          exams.map((exam) => (
            <ExamCard 
              key={exam.exam_id} 
              exam={exam} 
              onDelete={handleDeleteExam} 
            />
          ))
        )}
      </div>
    </div>
  );
}

export default MyExamsPage;