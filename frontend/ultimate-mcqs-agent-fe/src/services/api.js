import axios from 'axios';

// Tạo một instance (thể hiện) của axios
const api = axios.create({
  // URL trỏ đến backend FastAPI của bạn
  baseURL: 'http://127.0.0.1:8000', 
});

// Cấu hình Interceptor (Bộ lọc request)
api.interceptors.request.use(
  (config) => {
    // Lấy token từ localStorage
    const token = localStorage.getItem('authToken');
    
    // Nếu có token, thêm nó vào header 'Authorization'
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;