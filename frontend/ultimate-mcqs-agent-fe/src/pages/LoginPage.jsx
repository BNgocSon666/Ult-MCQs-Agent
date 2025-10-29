import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom'; // <--- Import Link
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

// === IMPORT FILE CSS ===
import './LoginPage.css'; 

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth(); 

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await api.post('/auth/login', formData, {
         headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      const { access_token } = response.data;
      const userData = { username: username }; 
      
      login(access_token, userData);
      navigate('/dashboard'); 

    } catch (err) {
      setError('Sai tên đăng nhập hoặc mật khẩu.');
    }
  };

  // === CẬP NHẬT CẤU TRÚC JSX ===
  return (
    <div className="login-page-container">
      <div className="login-form-container">
        <h2>Đăng nhập</h2>
        <form onSubmit={handleSubmit}>
          
          <div className="form-group">
            <label htmlFor="username">Username:</label>
            <input 
              id="username"
              type="text" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)} 
              required 
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password:</label>
            <input 
              id="password"
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              required 
            />
          </div>

          {error && <p className="error-message">{error}</p>}
          
          <button type="submit" className="login-button">
            Đăng nhập
          </button>
        </form>

        {/* === THÊM LINK ĐĂNG KÝ === */}
        <div className="register-link">
          Bạn chưa có tài khoản? <Link to="/register">Đăng ký ngay</Link>
        </div>

      </div>
    </div>
  );
}

export default LoginPage;