import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';

// === SỬ DỤNG CHUNG CSS VỚI TRANG LOGIN ===
import './LoginPage.css'; 

function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState(''); // <--- THÊM EMAIL
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('email', email); // <--- THÊM EMAIL
      formData.append('password', password);

      // === GỌI API ĐĂNG KÝ ===
      await api.post('/auth/register', formData, {
         headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      // Đăng ký thành công, thông báo và chuyển về trang login
      alert('Đăng ký thành công! Vui lòng đăng nhập.');
      navigate('/login'); 

    } catch (err) {
      if (err.response && err.response.data) {
        setError(err.response.data.detail || 'Lỗi xảy ra, vui lòng thử lại.');
      } else {
        setError('Lỗi kết nối máy chủ.');
      }
    }
  };

  return (
    <div className="login-page-container">
      <div className="login-form-container">
        <h2>Đăng ký tài khoản</h2> {/* <--- THAY ĐỔI TIÊU ĐỀ */}
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

          {/* === THÊM TRƯỜNG EMAIL === */}
          <div className="form-group">
            <label htmlFor="email">Email:</label>
            <input 
              id="email"
              type="email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
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
            Đăng ký
          </button>
        </form>

        {/* === THÊM LINK QUAY VỀ LOGIN === */}
        <div className="login-link">
          Đã có tài khoản? <Link to="/login">Đăng nhập</Link>
        </div>

      </div>
    </div>
  );
}

export default RegisterPage;