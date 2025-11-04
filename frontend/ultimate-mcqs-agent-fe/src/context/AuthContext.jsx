import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api'; // <--- Import axios

// 1. Tạo Context
const AuthContext = createContext();

// 2. Tạo "Trạm phát" (Provider)
export function AuthProvider({ children }) {
  // Lấy token ngay từ đầu
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [user, setUser] = useState(null);
  
  // === THÊM MỚI: State loading cho Auth ===
  const [isLoadingAuth, setIsLoadingAuth] = useState(true);

  // 3. Nâng cấp useEffect
  useEffect(() => {
    const fetchUserOnLoad = async () => {
      if (!token) {
        setIsLoadingAuth(false);
        return;
      }
      setIsLoadingAuth(true); 
      try {
        const response = await api.get('/users/me');
        setUser(response.data);
      } catch (error) {
        console.error("Token không hợp lệ, đang đăng xuất:", error);
        logout(); 
      } finally {
        setIsLoadingAuth(false);
      }
    };
    fetchUserOnLoad();
  }, [token]); // Chạy lại hàm này nếu token thay đổi

  // 4. Hàm đăng nhập (Giữ nguyên, nhưng tối ưu hơn)
  const login = (newToken) => {
    localStorage.setItem('authToken', newToken);
    setToken(newToken); // Set token cuối cùng để kích hoạt useEffect
  };

  // 5. Hàm đăng xuất (Giữ nguyên)
  const logout = () => {
    localStorage.removeItem('authToken');
    setToken(null);
    setUser(null);
  };

  const value = {
    token,
    user,
    login,
    logout,
    isAuthenticated: !!token,
    isLoadingAuth: isLoadingAuth, // <-- Truyền state loading ra ngoài
  };

  // === THÊM MỚI: Màn hình chờ trong khi xác thực ===
  // Tránh việc ProtectedRoute đưa về /login trong khi đang check
  if (isLoadingAuth) {
    return <div>Đang xác thực...</div>;
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// 6. Tạo custom hook `useAuth` (Giữ nguyên)
export function useAuth() {
  return useContext(AuthContext);
}