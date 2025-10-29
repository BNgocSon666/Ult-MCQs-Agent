import React, { createContext, useContext, useState, useEffect } from 'react';

// 1. Tạo Context
const AuthContext = createContext();

// 2. Tạo "Trạm phát" (Provider)
export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null); // Lưu thông tin user (id, username)

  // 3. Khi app mới tải, kiểm tra xem có token trong localStorage không
  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
      setToken(storedToken);
      // Bạn cũng có thể gọi API /users/me tại đây để lấy thông tin user
      // và set vào state 'user'
    }
  }, []);

  // 4. Hàm đăng nhập
  const login = (newToken, userData) => {
    setToken(newToken);
    setUser(userData); // Lưu thông tin user (ví dụ { id: 1, username: 'test' })
    localStorage.setItem('authToken', newToken);
  };

  // 5. Hàm đăng xuất
  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('authToken');
  };

  const value = {
    token,
    user,
    login,
    logout,
    isAuthenticated: !!token, // Biến tiện ích: true nếu đã đăng nhập
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// 6. Tạo custom hook `useAuth`
// Thay vì phải import useContext và AuthContext ở mọi nơi,
// chúng ta chỉ cần import `useAuth()`
export function useAuth() {
  return useContext(AuthContext);
}