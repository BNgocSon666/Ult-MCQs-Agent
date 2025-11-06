import React, { useState, useEffect } from "react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import "./ProfilePage.css";

function ProfilePage() {
  const { user } = useAuth();
  // const [isLoading, setIsLoading] = useState(true);

  // === 1. THÊM STATE MỚI ĐỂ QUẢN LÝ CHẾ ĐỘ ===
  const [isEditing, setIsEditing] = useState(false); // Mặc định là chế độ XEM
  const [originalData, setOriginalData] = useState({}); // Lưu dữ liệu gốc

  // State cho Form 1: Thông tin cá nhân
  const [profileData, setProfileData] = useState({
    full_name: "",
    email: "",
    phone_number: "",
    birth: "",
  });
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [profileMessage, setProfileMessage] = useState({ type: "", text: "" });

  // State cho Form 2: Đổi mật khẩu (Giữ nguyên)
  const [passwordData, setPasswordData] = useState({
    old_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [isSavingPassword, setIsSavingPassword] = useState(false);
  const [passwordMessage, setPasswordMessage] = useState({
    type: "",
    text: "",
  });

  // 2. CẬP NHẬT useEffect (Lưu dữ liệu gốc)
  // useEffect(() => {
  //   if (user) {
  //     setIsLoading(true);
  //     api
  //       .get(`/users/${user.user_id}`)
  //       .then((response) => {
  //         const data = {
  //           full_name: response.data.full_name || "",
  //           email: response.data.email || "",
  //           phone_number: response.data.phone_number || "",
  //           birth: response.data.birth ? response.data.birth.split("T")[0] : "",
  //         };
  //         setProfileData(data);
  //         setOriginalData(data); // <-- Lưu dữ liệu gốc
  //       })
  //       .catch((err) => {
  //         setProfileMessage({
  //           type: "error",
  //           text: "Không thể tải thông tin cá nhân.",
  //         });
  //       })
  //       .finally(() => {
  //         setIsLoading(false);
  //       });
  //   }
  // }, [user]);

  useEffect(() => {
    if (user) {
      // Dữ liệu này đến từ /users/me (auth_router.py đã sửa)
      const data = {
        full_name: user.full_name || "",
        email: user.email || "",
        phone_number: user.phone_number || "",
        birth: user.birth ? user.birth.split("T")[0] : "",
      };
      setProfileData(data);
      setOriginalData(data);
    }
  }, [user]);

  // (Hàm handleProfileChange, handlePasswordChange giữ nguyên)
  const handleProfileChange = (e) => {
    setProfileData({ ...profileData, [e.target.name]: e.target.value });
  };
  const handlePasswordChange = (e) => {
    setPasswordData({ ...passwordData, [e.target.name]: e.target.value });
  };

  // (Hàm handleProfileSubmit giữ nguyên)
  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setIsSavingProfile(true);
    setProfileMessage({ type: "", text: "" });

    const payload = new URLSearchParams();
    payload.append("full_name", profileData.full_name);
    payload.append("email", profileData.email);
    payload.append("phone_number", profileData.phone_number);
    if (profileData.birth) {
      payload.append("birth", profileData.birth);
    }

    try {
      const response = await api.put(`/users/${user.user_id}`, payload, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });
      setProfileMessage({
        type: "success",
        text: response.data.message || "Cập nhật thành công!",
      });
      setIsEditing(false); // <-- Tắt chế độ sửa sau khi lưu
      setOriginalData(profileData);
      window.location.reload(); // Cập nhật dữ liệu gốc
    } catch (err) {
      setProfileMessage({
        type: "error",
        text: err.response?.data?.detail || "Lỗi: Không thể cập nhật.",
      });
    } finally {
      setIsSavingProfile(false);
    }
  };

  // (Hàm handlePasswordSubmit giữ nguyên)
  const handlePasswordSubmit = async (e) => {
    // ... (Toàn bộ code handlePasswordSubmit giữ nguyên như trước)
    e.preventDefault();
    if (passwordData.new_password !== passwordData.confirm_password) {
      setPasswordMessage({ type: "error", text: "Mật khẩu mới không khớp!" });
      return;
    }
    setIsSavingPassword(true);
    setPasswordMessage({ type: "", text: "" });
    const payload = new URLSearchParams();
    payload.append("old_password", passwordData.old_password);
    payload.append("password", passwordData.new_password);
    try {
      await api.put(`/users/${user.user_id}`, payload, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });
      setPasswordMessage({ type: "success", text: "Đổi mật khẩu thành công!" });
      setPasswordData({
        old_password: "",
        new_password: "",
        confirm_password: "",
      });
    } catch (err) {
      setPasswordMessage({
        type: "error",
        text: err.response?.data?.detail || "Lỗi: Không thể đổi mật khẩu.",
      });
    } finally {
      setIsSavingPassword(false);
    }
  };

  // === 3. HÀM MỚI (Hủy chỉnh sửa) ===
  const handleCancelEdit = () => {
    setIsEditing(false);
    setProfileData(originalData); // Reset form về dữ liệu gốc
    setProfileMessage({ type: "", text: "" }); // Xóa thông báo
  };

  // if (isLoading) return <div className="loading-container">Đang tải...</div>;

  return (
    <div className="profile-page-container">
      {/* === CARD 1: THÔNG TIN CÁ NHÂN (ĐÃ CẬP NHẬT JSX) === */}
      <form onSubmit={handleProfileSubmit} className="profile-card">
        <h3>Thông tin cá nhân</h3>
        <p>Tên này sẽ được dùng để hiển thị trong kết quả bài thi.</p>

        {/* --- Hàng 1: Tên và Email --- */}
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="full_name">Tên đầy đủ</label>
            {isEditing ? (
              <input
                type="text"
                id="full_name"
                name="full_name"
                value={profileData.full_name}
                onChange={handleProfileChange}
                placeholder="Ví dụ: Bùi Ngọc Sơn"
              />
            ) : (
              <p className="view-mode-text">
                {profileData.full_name || "(Chưa cập nhật)"}
              </p>
            )}
          </div>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            {isEditing ? (
              <input
                type="email"
                id="email"
                name="email"
                value={profileData.email}
                onChange={handleProfileChange}
                required
              />
            ) : (
              <p className="view-mode-text">
                {profileData.email || "(Chưa cập nhật)"}
              </p>
            )}
          </div>
        </div>

        {/* --- Hàng 2: SĐT và Ngày sinh --- */}
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="phone_number">Số điện thoại</label>
            {isEditing ? (
              <input
                type="tel"
                id="phone_number"
                name="phone_number"
                value={profileData.phone_number}
                onChange={handleProfileChange}
              />
            ) : (
              <p className="view-mode-text">
                {profileData.phone_number || "(Chưa cập nhật)"}
              </p>
            )}
          </div>
          <div className="form-group">
            <label htmlFor="birth">Ngày sinh</label>
            {isEditing ? (
              <input
                type="date"
                id="birth"
                name="birth"
                value={profileData.birth}
                onChange={handleProfileChange}
              />
            ) : (
              // Hiển thị ngày sinh đã format
              <p className="view-mode-text">
                {profileData.birth
                  ? new Date(profileData.birth).toLocaleDateString("vi-VN")
                  : "(Chưa cập nhật)"}
              </p>
            )}
          </div>
        </div>

        {/* --- Footer (Nút bấm đã cập nhật) --- */}
        <div className="card-footer">
          {profileMessage.text && (
            <span className={`message ${profileMessage.type}`}>
              {profileMessage.text}
            </span>
          )}

          <div className="footer-buttons">
            {isEditing ? (
              <>
                <button
                  type="button"
                  className="edit-button cancel"
                  onClick={handleCancelEdit}
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="save-button"
                  disabled={isSavingProfile}
                >
                  {isSavingProfile ? "Đang lưu..." : "Lưu thay đổi"}
                </button>
              </>
            ) : (
              <button
                type="button"
                className="edit-button edit-mode"
                onClick={() => setIsEditing(true)}
              >
                Chỉnh sửa thông tin
              </button>
            )}
          </div>
        </div>
      </form>

      {/* === CARD 2: ĐỔI MẬT KHẨU (Giữ nguyên) === */}
      <form onSubmit={handlePasswordSubmit} className="profile-card">
        <h3>Bảo mật & Đăng nhập</h3>
        {/* ... (Tất cả input old_password, new_password, confirm_password giữ nguyên) ... */}
        <div className="form-group">
          <label htmlFor="old_password">Mật khẩu cũ</label>
          <input
            type="password"
            id="old_password"
            name="old_password"
            value={passwordData.old_password}
            onChange={handlePasswordChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="new_password">Mật khẩu mới</label>
          <input
            type="password"
            id="new_password"
            name="new_password"
            value={passwordData.new_password}
            onChange={handlePasswordChange}
            minLength="5"
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
