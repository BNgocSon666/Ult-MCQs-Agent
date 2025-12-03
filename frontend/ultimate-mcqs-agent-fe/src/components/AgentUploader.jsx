import React, { useState } from "react";
import api from "../services/api";
import "./AgentUploader.css";
import ReviewModal from "./ReviewModal";

function AgentUploader() {
  const [file, setFile] = useState(null);
  const [numQuestions, setNumQuestions] = useState(5);
  const [summaryMode, setSummaryMode] = useState("auto");

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const [apiResult, setApiResult] = useState(null);

  // === CẬP NHẬT HÀM XỬ LÝ CHỌN FILE ===
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    // Reset lỗi và file cũ mỗi khi chọn lại
    setError("");
    setFile(null);

    if (selectedFile) {
      // 1. Lấy đuôi file (Extension)
      const fileName = selectedFile.name;
      const fileExtension = fileName.split(".").pop().toLowerCase();

      // 2. Danh sách các đuôi cho phép (Khớp với Backend)
      const allowedExtensions = [
        "pdf",
        "docx",
        "doc",
        "txt",
        "mp3",
        "wav",
        "m4a",
      ];

      // 3. Kiểm tra định dạng
      if (!allowedExtensions.includes(fileExtension)) {
        setError(
          "❌ Định dạng file không hợp lệ! Chỉ hỗ trợ: PDF, DOCX, TXT, MP3, WAV, M4A."
        );
        e.target.value = null; // Reset ô input để người dùng chọn lại
        return; // Dừng lại, không setFile
      }

      // 4. (Tùy chọn) Kiểm tra dung lượng (Ví dụ giới hạn 20MB)
      const maxSizeMB = 20;
      if (selectedFile.size > maxSizeMB * 1024 * 1024) {
        setError(`❌ File quá lớn! Vui lòng tải file nhỏ hơn ${maxSizeMB}MB.`);
        e.target.value = null;
        return;
      }

      // Nếu tất cả đều ổn -> Lưu file vào state
      setFile(selectedFile);
    }
  };
  // ====================================

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Kiểm tra kỹ lại lần nữa trước khi gửi
    if (!file) {
      setError("Vui lòng chọn một file hợp lệ.");
      return;
    }

    setError("");
    setIsLoading(true);
    setApiResult(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("num_questions", numQuestions);
    formData.append("summary_mode", summaryMode);

    const fileType = file.type;
    // Logic xác định endpoint dựa trên loại file hoặc đuôi file
    let endpoint = "/agent/text";

    // Kiểm tra nếu là file âm thanh (dựa trên đuôi file cho chắc chắn)
    const audioExts = ["mp3", "wav", "m4a"];
    const ext = file.name.split(".").pop().toLowerCase();

    if (fileType.startsWith("audio/") || audioExts.includes(ext)) {
      endpoint = "/agent/audio";
    }

    try {
      const response = await api.post(endpoint, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setApiResult(response.data);
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data && err.response.data.detail) {
        // Hiển thị lỗi chi tiết từ Backend trả về
        setError(`❌ Lỗi từ server: ${err.response.data.detail}`);
      } else {
        setError("❌ Lỗi kết nối hoặc xử lý. Vui lòng thử lại.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="uploader-container">
      <h3>Tạo câu hỏi từ tài liệu</h3>
      <p>
        Tải lên file (PDF, DOCX, TXT, MP3, WAV) để AI tự động phân tích và tạo
        bộ câu hỏi trắc nghiệm.
      </p>

      <form onSubmit={handleSubmit} className="uploader-form">
        <div className="form-group">
          <label htmlFor="file-upload">Chọn file:</label>
          <input
            id="file-upload"
            type="file"
            // Thuộc tính accept giúp lọc file ngay ở cửa sổ chọn file của HĐH
            accept=".pdf,.docx,.doc,.txt,.mp3,.wav,.m4a"
            onChange={handleFileChange}
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="num-questions">Số câu hỏi (tối đa):</label>
            <input
              id="num-questions"
              type="number"
              value={numQuestions}
              onChange={(e) => setNumQuestions(e.target.value)}
              min="1"
              max="20"
            />
          </div>

          <div className="form-group">
            <label htmlFor="summary-mode">Chế độ tóm tắt:</label>
            <select
              id="summary-mode"
              value={summaryMode}
              onChange={(e) => setSummaryMode(e.target.value)}
            >
              <option value="auto">Tự động (Nếu dài)</option>
              <option value="force">Luôn luôn</option>
              <option value="none">Không bao giờ</option>
            </select>
          </div>
        </div>

        {/* Nút bấm bị vô hiệu hóa nếu chưa có file hoặc đang loading */}
        <button
          type="submit"
          className="upload-button"
          disabled={isLoading || !file}
        >
          {isLoading ? "Đang xử lý..." : "Bắt đầu tạo"}
        </button>

        {/* Hiển thị thông báo lỗi màu đỏ */}
        {error && (
          <p
            className="error-message"
            style={{ color: "red", marginTop: "10px", fontWeight: "bold" }}
          >
            {error}
          </p>
        )}
      </form>

      {apiResult && (
        <ReviewModal result={apiResult} onClose={() => setApiResult(null)} />
      )}
    </div>
  );
}

export default AgentUploader;
