import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function ProtectedRoute() {
  // Lấy cả 2 state từ AuthContext
  const { isAuthenticated, isLoadingAuth } = useAuth(); 

  // 1. Nếu đang kiểm tra, hiển thị màn hình chờ
  if (isLoadingAuth) {
    return <div>Đang kiểm tra đăng nhập...</div>;
  }

  // 2. Nếu kiểm tra xong và KHÔNG có token
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // 3. Nếu kiểm tra xong và CÓ token
  return <Outlet />;
}

export default ProtectedRoute;