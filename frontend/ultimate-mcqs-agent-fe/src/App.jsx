import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ProtectedRoute from './components/ProtectedRoute';

// Import các trang con
import AgentUploader from './components/AgentUploader'; 
import MyQuestionsPage from './pages/MyQuestionsPage'; 
import MyExamsPage from './pages/MyExamsPage';
import ExamBuilderPage from './pages/ExamBuilderPage'; 
import ExamDetailPage from './pages/ExamDetailPage';
import ExamStartPage from './pages/ExamStartPage';
import ExamTakerPage from './pages/ExamTakerPage';

function App() {
  return (
    <div className="App">
      <Routes>
        {/* === Các Route Công khai === */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/take/:share_token" element={<ExamStartPage />} />
        <Route path="/session/:session_id" element={<ExamTakerPage />} />
        
        {/* === Các Route Được Bảo Vệ === */}
        <Route element={<ProtectedRoute />}>
          
          <Route path="/dashboard" element={<DashboardPage />}>
            <Route index element={<Navigate to="agent" replace />} /> 
            <Route path="agent" element={<AgentUploader />} />
            <Route path="questions" element={<MyQuestionsPage />} />
            <Route path="exams" element={<MyExamsPage />} />
            <Route path="exams/new" element={<ExamBuilderPage />} />
            <Route path="exams/:exam_id" element={<ExamDetailPage />} />
          </Route>

        </Route>

        {/* Route mặc định */}
        <Route path="/" element={<Navigate to="/login" replace />} /> 
      </Routes>
    </div>
  );
}

export default App;