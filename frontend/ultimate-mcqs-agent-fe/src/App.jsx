import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom'; // <--- THÊM Navigate
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ProtectedRoute from './components/ProtectedRoute';

// === IMPORT CÁC TRANG CON CỦA DASHBOARD ===
import AgentUploader from './components/AgentUploader'; 
// (Tạo file này ở bước 3)
import MyQuestionsPage from './pages/MyQuestionsPage'; 
// (Tạo file này ở bước 3)
// import MyExamsPage from './pages/MyExamsPage'; 

function App() {
  return (
    <div className="App">
      <Routes>
        {/* === Các Route Công khai === */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* === Các Route Được Bảo Vệ === */}
        <Route element={<ProtectedRoute />}>
          
          {/* Thay đổi Route /dashboard */}
          <Route path="/dashboard" element={<DashboardPage />}>
            {/* Trang con mặc định của /dashboard */}
            <Route index element={<Navigate to="agent" replace />} /> 
            
            {/* Các trang con bên trong Dashboard */}
            <Route path="agent" element={<AgentUploader />} />
            <Route path="questions" element={<MyQuestionsPage />} />
            {/* <Route path="exams" element={<MyExamsPage />} /> */}
          </Route>

        </Route>

        {/* Route mặc định */}
        <Route path="/" element={<Navigate to="/login" replace />} /> 
      </Routes>
    </div>
  );
}

export default App;