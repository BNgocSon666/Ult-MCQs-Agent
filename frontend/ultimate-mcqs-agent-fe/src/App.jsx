import React from 'react';
import { Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <div className="App">
      <Routes>
        {/* === Các Route Công khai === */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* === Các Route Được Bảo Vệ === */}
        {/* Bọc các trang cần đăng nhập bằng ProtectedRoute */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          {/* Thêm các trang được bảo vệ khác ở đây (Giai đoạn 2) */}
          {/* <Route path="/agent-uploader" element={<... />} /> */}
        </Route>

        {/* Route mặc định (ví dụ: chuyển về login) */}
        <Route path="/" element={<LoginPage />} /> 
      </Routes>
    </div>
  );
}

export default App;