import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function ProtectedRoute() {
  const { isAuthenticated } = useAuth(); // Lấy trạng thái đăng nhập

  if (!isAuthenticated) {
    // Nếu chưa đăng nhập, điều hướng về trang /login
    return <Navigate to="/login" replace />;
  }

  // Nếu đã đăng nhập, hiển thị trang con (ví dụ: Dashboard)
  return <Outlet />;
}

export default ProtectedRoute;