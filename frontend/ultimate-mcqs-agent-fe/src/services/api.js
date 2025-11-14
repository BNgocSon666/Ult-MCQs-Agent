import axios from "axios";

<<<<<<< HEAD
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
//const API_BASE_URL = "http://127.0.0.1:8000";
=======
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
// const API_BASE_URL = "http://127.0.0.1:8000";
>>>>>>> 5b1e416 (lms 2)

// Tạo một instance (thể hiện) của axios
const api = axios.create({
  // URL trỏ đến backend FastAPI của bạn
  baseURL: API_BASE_URL,
});

// Cấu hình Interceptor (Bộ lọc request)
api.interceptors.request.use(
  (config) => {
    // Lấy token từ localStorage
    const token = localStorage.getItem("authToken");

    // Nếu có token, thêm nó vào header 'Authorization'
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
