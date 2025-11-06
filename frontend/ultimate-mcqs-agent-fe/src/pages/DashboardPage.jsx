import React from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate, NavLink, Outlet } from "react-router-dom";
import AgentUploader from "../components/AgentUploader";

import "./DashboardPage.css";

function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  // Hàm style cho NavLink
  const getNavLinkClass = ({ isActive }) => {
    return isActive ? "nav-link active" : "nav-link";
  };

  return (
    <div className="dashboard-layout">
      <header className="dashboard-header">
        <div className="header-left">
          {" "}
          {/* Bọc logo và nav */}
          {/* === THAY ĐỔI DÒNG NÀY === */}
          <div className="header-logo">
            {/* Thêm thẻ <img> trỏ đến file logo trong /public */}
            <img
              src="/logo2.png" /* <-- Đổi tên file nếu logo của bạn tên khác */
              alt="Logo"
              className="logo-image"
            />
            <span>Ultimate MCQs</span>
          </div>
          {/* === KẾT THÚC THAY ĐỔI === */}
          <nav className="dashboard-nav">
            <NavLink to="/dashboard/agent" className={getNavLinkClass}>
              Tạo mới (AI)
            </NavLink>
            <NavLink to="/dashboard/questions" className={getNavLinkClass}>
              Thư viện câu hỏi
            </NavLink>
            <NavLink to="/dashboard/exams" className={getNavLinkClass}>
              Đề thi của tôi
            </NavLink>
          </nav>
        </div>
        <div className="header-user">
          <span>Chào, {user ? user.full_name || user.username : "bạn"}!</span>

          {/* === THÊM NÚT MỚI NÀY === */}
          <NavLink to="/dashboard/profile" className="account-button">
            Tài khoản
          </NavLink>
          {/* === KẾT THÚC === */}

          <button onClick={handleLogout} className="logout-button">
            Đăng xuất
          </button>
        </div>
      </header>

      <main className="dashboard-main">
        {/* <AgentUploader /> */}
        <Outlet />
      </main>
    </div>
  );
}

export default DashboardPage;
