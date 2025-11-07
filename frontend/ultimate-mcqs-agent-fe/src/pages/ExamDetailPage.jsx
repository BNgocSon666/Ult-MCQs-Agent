import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../services/api";
import "./ExamDetailPage.css"; // Sẽ tạo ở bước 4

// Component con để hiển thị câu hỏi (chỉ xem)
function QuestionView({ question, index }) {
  const [options, setOptions] = useState([]);

  useEffect(() => {
    try {
      setOptions(JSON.parse(question.options || "[]"));
    } catch (e) {
      setOptions([]);
    }
  }, [question.options]);

  const getQuestionText = () => {
    try {
      return JSON.parse(question.question_text);
    } catch (e) {
      return question.question_text;
    }
  };

  return (
    <div className="question-view-item">
      <strong>Câu {index + 1}:</strong> {getQuestionText()}
      <ul className="question-view-options">
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
    </div>
  );
}

// Component Trang chính
function ExamDetailPage() {
  const [exam, setExam] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [results, setResults] = useState([]);

  // useParams lấy :exam_id từ URL
  const { exam_id } = useParams();

  const navigate = useNavigate();
  const [isExporting, setIsExporting] = useState(false); // <-- Dòng 1: State mới

  // <-- Dòng 2: Hàm xử lý mới
  const handleExportPdf = async () => {
    setIsExporting(true);
    try {
      // 1. Gọi API POST, yêu cầu kiểu 'blob'
      const response = await api.post(
        "/export/pdf",
        { exam_id: exam.exam_id },
        { responseType: "blob" }
      );

      // 2. Lấy tên file từ header Content-Disposition (ĐÃ TINH CHỈNH)
      const header = response.headers["content-disposition"];
      let filename = `Exam_${exam.exam_id}.pdf`; // Tên mặc định

      if (header) {
        // --- LOGIC MỚI: Ưu tiên tìm tên file được mã hóa UTF-8 ---
        const encodedMatch = header.match(/filename\*=UTF-8''([^;]+)/i);
        if (encodedMatch && encodedMatch[1]) {
          // Giải mã, xử lý khoảng trắng, và loại bỏ DẤU NGOẶC KÉP THỪA (Nếu có)
          filename = decodeURIComponent(
            encodedMatch[1].replace(/\+/g, " ")
          ).replace(/"/g, "");
        } else {
          // Fallback nếu không tìm thấy encoding UTF-8
          const basicMatch = header.match(/filename="([^"]+)"/i);
          if (basicMatch && basicMatch[1]) {
            filename = basicMatch[1];
          }
        }
      }

      // 3. Tạo URL tạm thời cho file blob
      const url = window.URL.createObjectURL(new Blob([response.data]));

      // 4. Tạo thẻ <a> ảo để kích hoạt tải xuống
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename); // Đặt tên file

      // 5. Kích hoạt và dọn dẹp
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url); // Giải phóng bộ nhớ
    } catch (err) {
      console.error("Lỗi khi xuất PDF:", err);
      alert("Không thể xuất PDF. Vui lòng thử lại.");
    } finally {
      setIsExporting(false);
    }
  };

  // 1. Tải chi tiết đề thi khi trang mở ra
  useEffect(() => {
    const fetchExamData = async () => {
      setIsLoading(true);
      try {
        // Gọi API lấy chi tiết Exam (giữ nguyên)
        const examDetailPromise = api.get(`/exams/${exam_id}`);

        // Gọi API lấy kết quả (mới)
        const examResultsPromise = api.get(`/exams/${exam_id}/results`);

        // Chờ cả hai hoàn thành
        const [detailResponse, resultsResponse] = await Promise.all([
          examDetailPromise,
          examResultsPromise,
        ]);

        setExam(detailResponse.data);
        setResults(resultsResponse.data.results || []);
      } catch (err) {
        setError("Không thể tải chi tiết đề thi hoặc kết quả.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchExamData();
  }, [exam_id]); // Chạy lại nếu exam_id thay đổi

  // 2. Hàm xử lý copy link
  const handleCopyLink = () => {
    // Tạo link chia sẻ (ví dụ: http://localhost:5173/take/...)
    // Chúng ta sẽ định nghĩa route /take/... ở Giai đoạn 4
    const shareLink = `${window.location.origin}/take/${exam.share_token}`;
    navigator.clipboard.writeText(shareLink);
    alert("Đã sao chép link làm bài!");
  };

  if (isLoading)
    return <div className="loading-container">Đang tải chi tiết...</div>;
  if (error) return <div className="error-container">{error}</div>;
  if (!exam)
    return <div className="loading-container">Không tìm thấy đề thi.</div>;

  // Lấy link PDF (Backend của bạn đã có /export-pdf)
  // Lưu ý: api.defaults.baseURL là 'http://127.0.0.1:8000'
  const pdfUrl = `${api.defaults.baseURL}/exams/${exam.exam_id}/export-pdf`;

  return (
    <div className="exam-detail-page">
      {/* --- Cột 1: Thông tin và Hành động --- */}
      <div className="exam-detail-sidebar">
        <button onClick={() => navigate(-1)} className="back-button">
          &larr; Quay lại danh sách
        </button>

        <div className="detail-card info-card">
          <h2>{exam.title}</h2>
          <p>{exam.description || "Không có mô tả."}</p>
        </div>

        <div className="detail-card actions-card">
          <h3>Chia sẻ</h3>
          <p>Gửi link này cho người khác để họ làm bài.</p>
          <input
            type="text"
            readOnly
            value={`${window.location.origin}/take/${exam.share_token}`}
            className="share-link-input"
          />
          <button onClick={handleCopyLink} className="action-button copy">
            Sao chép link
          </button>
        </div>

        <div className="detail-card actions-card">
          <h3>Xuất file</h3>
          <p>Lưu một bản PDF của đề thi (bao gồm đáp án).</p>
          {/* Nút này là một thẻ <a> để tải file, nhưng nó cần token.
              Vì thẻ <a> không tự gửi header, chúng ta cần 1 cách khác 
              (Hoặc là mở link ở tab mới, yêu cầu user đăng nhập bên đó)
          */}
          <button
            onClick={handleExportPdf}
            className="action-button pdf"
            disabled={isExporting}
          >
            {isExporting ? "Đang xuất..." : "Xuất ra PDF"}
          </button>
        </div>

        <div className="detail-card actions-card">
          <h3>Thống kê</h3>
          <p>Xem kết quả và điểm số của những người đã làm đề thi này.</p>
          <button
            onClick={() => setIsModalOpen(true)}
            className="action-button view-results"
            disabled={results.length === 0}
          >
            {results.length > 0
              ? `Xem ${results.length} kết quả`
              : "Chưa có kết quả"}
          </button>
        </div>
      </div>

      {/* --- Cột 2: Danh sách câu hỏi --- */}
      <div className="exam-detail-main">
        <h3>Nội dung đề thi ({exam.questions.length} câu)</h3>
        <div className="questions-list-view">
          {exam.questions.map((q, index) => (
            <QuestionView key={q.question_id} question={q} index={index} />
          ))}
        </div>
      </div>
      <ResultsModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        results={results}
        exam={exam}
      />
    </div>
  );
}

function ResultsModal({ isOpen, onClose, results, exam }) {
  if (!isOpen) return null;

  const calculateScaledScore = (score, total) => {
    if (total === 0) return 0; // Tránh chia cho 0
    const scaled = (score / total) * 10;
    // Làm tròn 1 chữ số thập phân (ví dụ: 8.82 -> 8.8)
    return Math.round(scaled * 10) / 10;
  };

  // Hàm tính tổng số câu hỏi (lấy từ exam detail)
  const getTotalQuestions = () => {
    return exam?.questions?.length || results[0]?.total_questions || 0;
  };
  const totalQuestions = getTotalQuestions();

  return (
    <div className="modal-backdrop-results" onClick={onClose}>
      <div
        className="modal-content-results"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header-results">
          <h3>Kết quả làm bài: {exam.title}</h3>
          <button onClick={onClose} className="modal-close-button">
            &times;
          </button>
        </div>
        <div className="modal-body-results">
          {results.length > 0 ? (
            <table className="results-table">
              <thead>
                <tr>
                  <th>Người làm bài</th>
                  <th>Ngày làm</th>
                  <th>Ngày nộp</th>
                  <th>Số câu đúng</th>
                  <th>Tổng điểm</th>
                </tr>
              </thead>
              <tbody>
                {results.map((res) => (
                  <tr key={res.session_id}>
                    <td>{res.taker_name || "Khách"}</td>
                    <td>{new Date(res.start_time).toLocaleString("vi-VN")}</td>
                    <td>{new Date(res.end_time).toLocaleString("vi-VN")}</td>
                    <td>
                      {res.total_score} / {totalQuestions} {/* Cột điểm cũ */}
                    </td>
                    <td>
                      {/* THÊM Ô MỚI NÀY */}
                      {calculateScaledScore(res.total_score, totalQuestions)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>Chưa có ai nộp bài cho đề thi này.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default ExamDetailPage;
