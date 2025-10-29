import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import AgentUploader from '../components/AgentUploader'; // <--- IMPORT

// CSS cho layout mới
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
      
      {/* 1. Thanh điều hướng (Header) */}
      <header className="dashboard-header">
        <div className="header-logo">
          Ultimate MCQs
        </div>
        <div className="header-user">
          <span>Chào, {user ? user.username : 'bạn'}!</span>
          <button onClick={handleLogout} className="logout-button">
            Đăng xuất
          </button>
        </div>
      </header>
      
      {/* 2. Nội dung chính của trang */}
      <main className="dashboard-main">
        <AgentUploader />
      </main>

    </div>
  );
}

export default DashboardPage;