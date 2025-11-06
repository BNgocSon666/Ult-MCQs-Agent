import React, { useState, useEffect } from "react";
import api from "../services/api";
import "./MyQuestionsPage.css"; // Dùng file CSS bạn đã cung cấp
import { useAuth } from "../context/AuthContext";

// ==========================================================
// === COMPONENT CON (GIỮ NGUYÊN TỪ FILE CỦA BẠN) ===
// ==========================================================
function QuestionCard({ question, onDelete, onEdit }) {
  // Thêm onEdit
  const [options, setOptions] = useState([]);

  useEffect(() => {
    try {
      setOptions(JSON.parse(question.options || "[]"));
    } catch (e) {
      setOptions(["Lỗi parse options"]);
    }
  }, [question.options]);

  const getQuestionText = () => {
    try {
      return JSON.parse(question.question_text);
    } catch (e) {
      return question.question_text;
    }
  };

  const handleDelete = () => {
    if (window.confirm("Bạn có chắc muốn xóa câu hỏi này?")) {
      onDelete(question.question_id);
    }
  };

  const statusClass = question.status_by_agent || "need_review";

  return (
    <div className="my-question-card">
      <div className="card-q-text">{getQuestionText()}</div>
      <ul className="card-q-options">
        {options.map((opt, i) => {
          const letter = String.fromCharCode(65 + i);
          return (
            <li
              key={i}
              className={letter === question.answer_letter ? "correct" : ""}
            >
              {opt}
            </li>
          );
        })}
      </ul>

      {/* === FOOTER ĐÃ ĐƯỢC CẬP NHẬT THEO YÊU CẦU CỦA BẠN === */}
      <div className="card-q-footer">
        {/* Bên trái: Điểm và Trạng thái */}
        <div className="q-footer-left">
          <span>
            Điểm AI: <strong>{question.total_score || 0}</strong>
          </span>
          <span className={`q-status status-${statusClass}`}>
            {statusClass.replace("_", " ")}
          </span>
        </div>

        {/* Bên phải: Nút Sửa và Xóa */}
        <div className="card-q-actions">
          <button
            className="q-action-btn edit"
            onClick={() => onEdit(question.question_id)}
          >
            Sửa
          </button>
          <button className="q-action-btn delete" onClick={handleDelete}>
            Xóa
          </button>
        </div>
      </div>
    </div>
  );
}

// ==========================================================
// === COMPONENT THANH LỌC (MỚI) ===
// ==========================================================
function FilterBar({ onFilterSubmit }) {
  const [myFiles, setMyFiles] = useState([]);
  const [filters, setFilters] = useState({
    search_term: "",
    search_in_question: true,
    search_in_options: false,
    file_id: "",
    status: "",
    start_date: "",
    end_date: "",
    sort_by: "newest",
  });

  // Tải danh sách file cho bộ lọc
  useEffect(() => {
    const loadFiles = async () => {
      try {
        const response = await api.get("/agent/files/my-list"); // API mới
        setMyFiles(response.data.files || []);
      } catch (err) {
        console.error("Lỗi tải danh sách file:", err);
      }
    };
    loadFiles();
  }, []);

  const handleFilterChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onFilterSubmit(filters); // Gửi bộ lọc lên component Cha
  };

  return (
    <form className="filter-bar" onSubmit={handleSubmit}>
      <h3>Bộ lọc thư viện</h3>

      {/* Hàng 1: Tìm kiếm */}
      <div className="filter-group search-group">
        <input
          type="text"
          name="search_term"
          placeholder="Tìm kiếm theo từ khóa..."
          value={filters.search_term}
          onChange={handleFilterChange}
          className="search-input"
        />
        <div className="checkbox-group">
          <label>
            <input
              type="checkbox"
              name="search_in_question"
              checked={filters.search_in_question}
              onChange={handleFilterChange}
            />
            Trong câu hỏi
          </label>
          <label>
            <input
              type="checkbox"
              name="search_in_options"
              checked={filters.search_in_options}
              onChange={handleFilterChange}
            />
            Trong câu trả lời
          </label>
        </div>
      </div>

      {/* Hàng 2: Lọc */}
      <div className="filter-row">
        <div className="filter-group">
          <label>Lọc theo file</label>
          <select
            name="file_id"
            value={filters.file_id}
            onChange={handleFilterChange}
          >
            <option value="">Tất cả các file</option>
            {myFiles.map((file) => (
              <option key={file.file_id} value={file.file_id}>
                {file.filename}
              </option>
            ))}
          </select>
        </div>
        <div className="filter-group">
          <label>Lọc theo trạng thái</label>
          <select
            name="status"
            value={filters.status}
            onChange={handleFilterChange}
          >
            <option value="">Tất cả trạng thái</option>
            <option value="accepted">Accepted</option>
            <option value="need_review">Need Review</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
        <div className="filter-group">
          <label>Sắp xếp theo</label>
          <select
            name="sort_by"
            value={filters.sort_by}
            onChange={handleFilterChange}
          >
            <option value="newest">Mới nhất</option>
            <option value="oldest">Cũ nhất</option>
            <option value="score_high">Điểm AI cao</option>
            <option value="score_low">Điểm AI thấp</option>
          </select>
        </div>
      </div>

      {/* Hàng 3: Lọc theo ngày */}
      <div className="filter-row">
        <div className="filter-group">
          <label>Từ ngày</label>
          <input
            type="date"
            name="start_date"
            value={filters.start_date}
            onChange={handleFilterChange}
          />
        </div>
        <div className="filter-group">
          <label>Đến ngày</label>
          <input
            type="date"
            name="end_date"
            value={filters.end_date}
            onChange={handleFilterChange}
          />
        </div>
      </div>

      <div className="filter-actions">
        <button type="submit" className="filter-button">
          Áp dụng bộ lọc
        </button>
      </div>
    </form>
  );
}

// ==========================================================
// === COMPONENT CHA (ĐÃ NÂNG CẤP) ===
// ==========================================================
function MyQuestionsPage() {
  const [questions, setQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [totalCount, setTotalCount] = useState(0); // <-- Thêm state đếm
  const { user } = useAuth();

  // Hàm gọi API (đã nâng cấp)
  const fetchQuestions = async (filters = {}) => {
    setIsLoading(true);

    // Xây dựng params, chỉ gửi đi những giá trị có thật
    const params = {};
    if (filters.search_term) params.search_term = filters.search_term;
    params.search_in_question = filters.search_in_question !== false; // Gửi true nếu tick
    params.search_in_options = filters.search_in_options === true; // Gửi true nếu tick
    if (filters.file_id) params.file_id = filters.file_id;
    if (filters.status) params.status = filters.status;
    if (filters.start_date) params.start_date = filters.start_date;
    if (filters.end_date) params.end_date = filters.end_date;
    params.sort_by = filters.sort_by || "newest";

    try {
      const response = await api.get("/questions", { params });
      setQuestions(response.data.questions || []);
      setTotalCount(response.data.count || 0);
    } catch (err) {
      setError("Không thể tải thư viện câu hỏi.");
    } finally {
      setIsLoading(false);
    }
  };

  // Gọi API khi component được tải (chỉ 1 lần)
  useEffect(() => {
    if (user) {
      fetchQuestions(); // Gọi lần đầu với bộ lọc rỗng
    }
  }, [user]);

  // Hàm xử lý xóa (giữ nguyên)
  const handleDeleteQuestion = async (questionId) => {
    try {
      await api.delete(`/questions/${questionId}`);
      // Cập nhật lại UI sau khi xóa
      setQuestions((prevQuestions) =>
        prevQuestions.filter((q) => q.question_id !== questionId)
      );
      setTotalCount((prevCount) => prevCount - 1);
    } catch (err) {
      alert("Lỗi: Không thể xóa câu hỏi.");
    }
  };

  // Hàm xử lý sửa (chưa làm)
  const handleEditQuestion = (questionId) => {
    alert(`Chức năng Sửa cho câu hỏi ID: ${questionId} (Chưa làm)`);
    // (Trong tương lai, bạn sẽ mở Modal hoặc chuyển trang tại đây)
  };

  if (error) return <div className="error-container">{error}</div>;

  return (
    <div className="my-questions-page">
      {/* Header cũ của bạn, đã cập nhật số lượng */}
      <div className="page-header">
        <h2>Thư viện câu hỏi của tôi</h2>
        <p>
          Hiển thị: {questions.length} / Tổng cộng: {totalCount} câu hỏi
        </p>
      </div>

      {/* Thanh Lọc Mới */}
      <FilterBar onFilterSubmit={fetchQuestions} />

      {/* Danh sách câu hỏi */}
      <div className="questions-list-container">
        {isLoading ? (
          <div className="loading-container">Đang tải...</div>
        ) : questions.length === 0 ? (
          <p>Không tìm thấy câu hỏi nào phù hợp với bộ lọc.</p>
        ) : (
          questions.map((q) => (
            <QuestionCard
              key={q.question_id}
              question={q}
              onDelete={handleDeleteQuestion}
              onEdit={handleEditQuestion}
            />
          ))
        )}
      </div>
    </div>
  );
}

export default MyQuestionsPage;
