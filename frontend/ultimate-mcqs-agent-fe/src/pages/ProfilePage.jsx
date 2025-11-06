import React, { useState, useEffect } from "react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";
// Tạo file CSS này ở Bước 2
import "./ProfilePage.css";

function ProfilePage() {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);

  // === State cho Form 1: Thông tin cá nhân ===
  const [profileData, setProfileData] = useState({
    full_name: "",
    email: "",
    phone_number: "",
    dob: "",
  });
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [profileMessage, setProfileMessage] = useState({ type: "", text: "" });

  // === State cho Form 2: Đổi mật khẩu ===
  const [passwordData, setPasswordData] = useState({
    new_password: "",
    confirm_password: "",
  });
  const [isSavingPassword, setIsSavingPassword] = useState(false);
  const [passwordMessage, setPasswordMessage] = useState({
    type: "",
    text: "",
  });

  // 1. Tải thông tin user hiện tại khi trang mở
  useEffect(() => {
    if (user) {
      setIsLoading(true);
      api
        .get(`/users/${user.user_id}`)
        .then((response) => {
          setProfileData({
            full_name: response.data.full_name || "",
            email: response.data.email || "",
            phone_number: response.data.phone_number || "",
            // Cần format lại ngày YYYY-MM-DD cho input type="date"
            dob: response.data.dob ? response.data.dob.split("T")[0] : "",
          });
        })
        .catch((err) => {
          setProfileMessage({
            type: "error",
            text: "Không thể tải thông tin cá nhân.",
          });
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [user]);

  // 2. Xử lý thay đổi form thông tin
  const handleProfileChange = (e) => {
    setProfileData({ ...profileData, [e.target.name]: e.target.value });
  };

  // 3. Xử lý thay đổi form mật khẩu
  const handlePasswordChange = (e) => {
    setPasswordData({ ...passwordData, [e.target.name]: e.target.value });
  };

  // 4. GỬI FORM 1: Cập nhật thông tin
  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setIsSavingProfile(true);
    setProfileMessage({ type: "", text: "" });

    // Backend (users_router.py) cần Form data
    const payload = new URLSearchParams();
    payload.append("full_name", profileData.full_name);
    payload.append("email", profileData.email);
    payload.append("phone_number", profileData.phone_number);
    payload.append("dob", profileData.dob);

    try {
      await api.put(`/users/${user.user_id}`, payload, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });
      setProfileMessage({
        type: "success",
        text: "Cập nhật thông tin thành công!",
      });
    } catch (err) {
      setProfileMessage({ type: "error", text: "Lỗi: Không thể cập nhật." });
    } finally {
      setIsSavingProfile(false);
    }
  };

  // 5. GỬI FORM 2: Đổi mật khẩu
  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (passwordData.new_password !== passwordData.confirm_password) {
      setPasswordMessage({ type: "error", text: "Mật khẩu mới không khớp!" });
      return;
    }

    setIsSavingPassword(true);
    setPasswordMessage({ type: "", text: "" });

    const payload = new URLSearchParams();
    payload.append("password", passwordData.new_password);

    try {
      await api.put(`/users/${user.user_id}`, payload, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });
      setPasswordMessage({ type: "success", text: "Đổi mật khẩu thành công!" });
      setPasswordData({ new_password: "", confirm_password: "" }); // Xóa form
    } catch (err) {
      setPasswordMessage({
        type: "error",
        text: "Lỗi: Không thể đổi mật khẩu.",
      });
    } finally {
      setIsSavingPassword(false);
    }
  };

  if (isLoading) return <div className="loading-container">Đang tải...</div>;

  return (
    <div className="profile-page-container">
      {/* === CARD 1: THÔNG TIN CÁ NHÂN === */}
      <form onSubmit={handleProfileSubmit} className="profile-card">
        <h3>Thông tin cá nhân</h3>
        <p>Tên này sẽ được dùng để hiển thị trong kết quả bài thi.</p>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="full_name">Tên đầy đủ</label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={profileData.full_name}
              onChange={handleProfileChange}
              placeholder="Ví dụ: Bùi Ngọc Sơn"
            />
          </div>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={profileData.email}
              onChange={handleProfileChange}
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="phone_number">Số điện thoại</label>
            <input
              type="tel"
              id="phone_number"
              name="phone_number"
              value={profileData.phone_number}
              onChange={handleProfileChange}
            />
          </div>
          <div className="form-group">
            <label htmlFor="dob">Ngày sinh</label>
            <input
              type="date"
              id="dob"
              name="dob"
              value={profileData.dob}
              onChange={handleProfileChange}
            />
          </div>
        </div>

        <div className="card-footer">
          {profileMessage.text && (
            <span className={`message ${profileMessage.type}`}>
              {profileMessage.text}
            </span>
          )}
          <button
            type="submit"
            className="save-button"
            disabled={isSavingProfile}
          >
            {isSavingProfile ? "Đang lưu..." : "Lưu thay đổi"}
          </button>
        </div>
      </form>

      {/* === CARD 2: ĐỔI MẬT KHẨU === */}
      <form onSubmit={handlePasswordSubmit} className="profile-card">
        <h3>Bảo mật & Đăng nhập</h3>

        <div className="form-group">
          <label htmlFor="new_password">Mật khẩu mới</label>
          <input
            type="password"
            id="new_password"
            name="new_password"
            value={passwordData.new_password}
            onChange={handlePasswordChange}
            minLength="6"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="confirm_password">Xác nhận mật khẩu mới</label>
          <input
            type="password"
            id="confirm_password"
            name="confirm_password"
            value={passwordData.confirm_password}
            onChange={handlePasswordChange}
            required
          />
        </div>

        <div className="card-footer">
          {passwordMessage.text && (
            <span className={`message ${passwordMessage.type}`}>
              {passwordMessage.text}
            </span>
          )}
          <button
            type="submit"
            className="save-button"
            disabled={isSavingPassword}
          >
            {isSavingPassword ? "Đang lưu..." : "Đổi mật khẩu"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ProfilePage;
