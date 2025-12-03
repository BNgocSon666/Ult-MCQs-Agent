import React, { useState, useEffect } from "react";
import api from "../services/api";
import "./MyQuestionsPage.css"; // Dùng file CSS bạn đã cung cấp
import { useAuth } from "../context/AuthContext";

// ==========================================================
// === COMPONENT CON (GIỮ NGUYÊN TỪ FILE CỦA BẠN) ===
// ==========================================================

const getStatusLabel = (status) => {
  switch (status) {
    case "accepted":
      return "Đạt chuẩn"; // Hoặc: Tốt, Duyệt
    case "need_review":
      return "Cần xem lại"; // Hoặc: Khá
    case "rejected":
      return "Kém"; // Hoặc: Loại bỏ
    default:
      return "Chưa rõ";
  }
};

function QuestionCard({ question, onDelete, onEdit }) {
  // <-- Nhận onEdit
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

      <div className="card-q-footer">
        <div className="q-footer-left">
          <span>
            Điểm AI: <strong>{question.total_score || 0}</strong>
          </span>
          <span className={`q-status status-${statusClass}`}>
            {getStatusLabel(statusClass)}
          </span>
        </div>

        <div className="card-q-actions">
          {/* CẬP NHẬT onEdit: Gửi cả object question lên */}
          <button
            className="q-action-btn edit"
            onClick={() => onEdit(question)}
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

function PaginationControls({ currentPage, totalPages, onPageChange }) {
  const pageNumbers = [];
  // Logic để chỉ hiển thị tối đa 5 nút số (ví dụ: 1, 2, 3, 4, 5 hoặc ..., 4, 5, 6, 7, ...)
  const maxPagesToShow = 5;
  let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
  let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

  if (endPage - startPage + 1 < maxPagesToShow) {
    startPage = Math.max(1, endPage - maxPagesToShow + 1);
  }

  for (let i = startPage; i <= endPage; i++) {
    pageNumbers.push(i);
  }

  if (totalPages <= 1) return null; // Không hiển thị nếu chỉ có 1 trang

  return (
    <div className="pagination-controls">
      {/* Nút Về đầu */}
      <button onClick={() => onPageChange(1)} disabled={currentPage === 1}>
        &laquo; Đầu
      </button>
      {/* Nút Lùi */}
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
      >
        &lsaquo; Trước
      </button>

      {/* Các nút số */}
      {startPage > 1 && <span className="page-ellipsis">...</span>}
      {pageNumbers.map((number) => (
        <button
          key={number}
          onClick={() => onPageChange(number)}
          className={`page-number ${number === currentPage ? "active" : ""}`}
        >
          {number}
        </button>
      ))}
      {endPage < totalPages && <span className="page-ellipsis">...</span>}

      {/* Nút Tiến */}
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        Sau &rsaquo;
      </button>
      {/* Nút Về cuối */}
      <button
        onClick={() => onPageChange(totalPages)}
        disabled={currentPage === totalPages}
      >
        Cuối &raquo;
      </button>
    </div>
  );
}

function QuestionEditModal({ questionToEdit, onClose, onSaveSuccess }) {
  // 1. State nội bộ của Modal để quản lý form
  const [editData, setEditData] = useState({
    question_text: "",
    options: [],
    answer_letter: "",
  });
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  // 2. Hàm parse text (vì text trong DB là JSON string)
  const parseJsonText = (text) => {
    try {
      return JSON.parse(text);
    } catch (e) {
      return text;
    }
  };

  // 3. useEffect: Load dữ liệu vào form khi Modal được mở
  useEffect(() => {
    if (questionToEdit) {
      setEditData({
        question_text: parseJsonText(questionToEdit.question_text),
        options: parseJsonText(questionToEdit.options || "[]"),
        answer_letter: questionToEdit.answer_letter || "A",
      });
    }
  }, [questionToEdit]); // Chạy lại khi 'questionToEdit' thay đổi

  // 4. Các hàm xử lý thay đổi form
  const handleChange = (e) => {
    const { name, value } = e.target;
    setEditData((prev) => ({ ...prev, [name]: value }));
  };

  const handleOptionChange = (index, value) => {
    const newOptions = [...editData.options];
    newOptions[index] = value;
    setEditData((prev) => ({ ...prev, options: newOptions }));
  };

  // 5. Hàm LƯU (Quan trọng)
  const handleSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setError("");

    // Backend (questions_router.py) cần Form data và JSON string
    try {
      const formData = new URLSearchParams();
      formData.append("question_text", JSON.stringify(editData.question_text));
      formData.append("options_json", JSON.stringify(editData.options));
      formData.append("answer_letter", editData.answer_letter);

      // Gọi API PUT
      await api.put(`/questions/${questionToEdit.question_id}`, formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      onSaveSuccess(); // Báo cho Cha biết đã lưu xong để tải lại
    } catch (err) {
      setError("Lỗi khi lưu. Vui lòng thử lại.");
    } finally {
      setIsSaving(false);
    }
  };

  if (!questionToEdit) return null;

  // 6. Giao diện (JSX) của Modal
  return (
    <div className="edit-modal-backdrop" onClick={onClose}>
      <div className="edit-modal-content" onClick={(e) => e.stopPropagation()}>
        <form onSubmit={handleSave}>
          <div className="edit-modal-header">
            <h3>Chỉnh sửa câu hỏi (ID: {questionToEdit.question_id})</h3>
            <button
              type="button"
              onClick={onClose}
              className="edit-modal-close"
            >
              &times;
            </button>
          </div>

          <div className="edit-modal-body">
            {/* Sửa Câu hỏi */}
            <div className="edit-form-group">
              <label>Nội dung câu hỏi:</label>
              <textarea
                name="question_text"
                value={editData.question_text}
                onChange={handleChange}
                rows="4"
                required
              />
            </div>

            {/* Sửa Lựa chọn */}
            <div className="edit-form-group">
              <label>Các lựa chọn & Đáp án đúng:</label>
              <div className="edit-options-list">
                {editData.options.map((opt, i) => {
                  const letter = String.fromCharCode(65 + i); // A, B, C, D
                  return (
                    <div className="edit-option-item" key={i}>
                      <input
                        type="radio"
                        name="answer_letter" // Cùng name để chọn 1
                        value={letter}
                        checked={editData.answer_letter === letter}
                        onChange={handleChange}
                      />
                      <input
                        type="text"
                        value={opt}
                        onChange={(e) => handleOptionChange(i, e.target.value)}
                        required
                        className="edit-option-input"
                      />
                    </div>
                  );
                })}
              </div>
            </div>

            {error && <p className="error-message">{error}</p>}
          </div>

          <div className="edit-modal-footer">
            <button
              type="button"
              className="edit-button cancel"
              onClick={onClose}
            >
              Hủy
            </button>
            <button
              type="submit"
              className="edit-button save"
              disabled={isSaving}
            >
              {isSaving ? "Đang lưu..." : "Lưu thay đổi"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ==========================================================
// === COMPONENT CHA (ĐÃ NÂNG CẤP) ===
// ==========================================================
function MyQuestionsPage() {
  const [questions, setQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const [currentFilters, setCurrentFilters] = useState({});
  const [pagination, setPagination] = useState({
    current_page: 1,
    total_pages: 1,
    page_size: 10,
    total_count: 0,
  });
  const { user } = useAuth();

  // === STATE MỚI ĐỂ QUẢN LÝ MODAL ===
  const [editingQuestion, setEditingQuestion] = useState(null); // null = đóng

  // Hàm gọi API (đã nâng cấp)
  const fetchQuestions = async (filters = currentFilters, page = 1) => {
    setIsLoading(true);
    // ... (Code fetchQuestions giữ nguyên như trước) ...
    const params = {
      search_in_question: filters.search_in_question !== false,
      search_in_options: filters.search_in_options === true,
      sort_by: filters.sort_by || "newest",
      page: page,
      page_size: 10,
    };
    if (filters.search_term) params.search_term = filters.search_term;
    if (filters.file_id) params.file_id = filters.file_id;
    if (filters.status) params.status = filters.status;
    if (filters.start_date) params.start_date = filters.start_date;
    if (filters.end_date) params.end_date = filters.end_date;

    try {
      const response = await api.get("/questions", { params });
      setQuestions(response.data.questions || []);
      setPagination({
        total_count: response.data.total_count || 0,
        page_size: response.data.page_size || 10,
        current_page: response.data.current_page || 1,
        total_pages: Math.ceil(
          (response.data.total_count || 0) / (response.data.page_size || 10)
        ),
      });
    } catch (err) {
      setError("Không thể tải thư viện câu hỏi.");
    } finally {
      setIsLoading(false);
    }
  };

  // Gọi API khi component được tải (giữ nguyên)
  useEffect(() => {
    if (user) {
      fetchQuestions({}, 1);
    }
  }, [user]);

  // Hàm xử lý khi bấm "Áp dụng bộ lọc"
  const handleFilterSubmit = (filters) => {
    setCurrentFilters(filters);
    fetchQuestions(filters, 1);
  };

  // Hàm xử lý khi bấm nút Phân trang
  const handlePageChange = (newPage) => {
    fetchQuestions(currentFilters, newPage);
  };

  // Hàm xử lý xóa (giữ nguyên)
  const handleDeleteQuestion = async (questionId) => {
    try {
      await api.delete(`/questions/${questionId}`);
      fetchQuestions(currentFilters, pagination.current_page);
    } catch (err) {
      alert("Lỗi: Không thể xóa câu hỏi.");
    }
  };

  // === HÀM XỬ LÝ SỬA MỚI ===
  const handleEditQuestion = (question) => {
    setEditingQuestion(question); // Mở Modal bằng cách set state
  };

  // === HÀM XỬ LÝ KHI LƯU THÀNH CÔNG ===
  const handleSaveSuccess = () => {
    setEditingQuestion(null); // Đóng Modal
    // Tải lại dữ liệu trang hiện tại để thấy thay đổi
    fetchQuestions(currentFilters, pagination.current_page);
  };

  if (error) return <div className="error-container">{error}</div>;

  return (
    <div className="my-questions-page">
      <div className="page-header">
        <h2>Thư viện câu hỏi của tôi</h2>
        <p>
          Hiển thị: {questions.length}/ Tổng cộng: {pagination.total_count} câu
          hỏi (Trang {pagination.current_page} / {pagination.total_pages})
        </p>
      </div>

      {/* Thanh Lọc (Giữ nguyên) */}
      <FilterBar onFilterSubmit={handleFilterSubmit} />

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
              onEdit={handleEditQuestion} // <-- Đã kết nối hàm Sửa
            />
          ))
        )}
      </div>

      {/* Phân trang (Giữ nguyên) */}
      <PaginationControls
        currentPage={pagination.current_page}
        totalPages={pagination.total_pages}
        onPageChange={handlePageChange}
      />

      {/* === RENDER MODAL (NẾU ĐANG SỬA) === */}
      {editingQuestion && (
        <QuestionEditModal
          questionToEdit={editingQuestion}
          onClose={() => setEditingQuestion(null)}
          onSaveSuccess={handleSaveSuccess}
        />
      )}
    </div>
  );
}

export default MyQuestionsPage;
