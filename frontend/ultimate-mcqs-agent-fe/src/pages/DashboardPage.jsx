import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import AgentUploader from '../components/AgentUploader'; 

import './DashboardPage.css';

function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="dashboard-layout">
      
      <header className="dashboard-header">
        
        {/* === THAY ĐỔI DÒNG NÀY === */}
        <div className="header-logo">
          {/* Thêm thẻ <img> trỏ đến file logo trong /public */}
          <img 
            src="/logo2.png"  /* <-- Đổi tên file nếu logo của bạn tên khác */
            alt="Logo" 
            className="logo-image" 
          />
          <span>Ultimate MCQs</span>
        </div>
        {/* === KẾT THÚC THAY ĐỔI === */}

        <div className="header-user">
          <span>Chào, {user ? user.username : 'bạn'}!</span>
          <button onClick={handleLogout} className="logout-button">
            Đăng xuất
          </button>
        </div>
      </header>
      
      <main className="dashboard-main">
        <AgentUploader />
      </main>

    </div>
  );
}

export default DashboardPage;