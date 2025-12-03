import React, { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import api from "../services/api";
import "./ExamResultsPage.css"; // Sẽ tạo ở bước 2

// Component con hiển thị 1 câu trả lời
function ResultQuestion({ question, index }) {
  const [options, setOptions] = useState([]);

  // Parse options và question_text (vì chúng là JSON)
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

  const { answer_letter, selected_option, is_correct } = question;

  return (
    <div
      className={`result-question-card ${is_correct ? "correct" : "incorrect"}`}
    >
      <div className="result-question-text">
        <strong>Câu {index + 1}:</strong> {getQuestionText()}
      </div>

      <ul className="result-options-list">
        {options.map((opt, i) => {
          const letter = String.fromCharCode(65 + i); // A, B, C, D
          let className = "";

          if (letter === answer_letter) {
            className = "is-correct-answer"; // Đây là đáp án đúng
          } else if (letter === selected_option) {
            className = "is-wrong-selection"; // Đây là đáp án sai mà user chọn
          }

          return (
            <li key={letter} className={className}>
              {opt}
            </li>
          );
        })}
      </ul>

      <div className="result-footer">
        {is_correct ? (
          <span>
            Bạn đã chọn đúng: <strong>{selected_option}</strong>
          </span>
        ) : (
          <span>
            Bạn đã chọn: <strong>{selected_option || "(Bỏ qua)"}</strong> | Đáp
            án đúng: <strong>{answer_letter}</strong>
          </span>
        )}
      </div>
    </div>
  );
}

// Component Trang chính
function ExamResultsPage() {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const { session_id } = useParams();
  const navigate = useNavigate();
  const location = useLocation(); // Dùng để lấy điểm số

  // Lấy điểm số từ trang trước (ExamTakerPage)
  const score = location.state?.score;
  const totalQuestions = results.length;

  // 1. Tải chi tiết kết quả
  useEffect(() => {
    const fetchResults = async () => {
      setIsLoading(true);
      setError("");
      try {
        const response = await api.get(`/sessions/${session_id}/results`);
        setResults(response.data || []);
      } catch (err) {
        setError("Không thể tải kết quả. Phiên làm bài không tồn tại.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchResults();
  }, [session_id]);

  if (isLoading)
    return <div className="loading-container">Đang tải kết quả...</div>;
  if (error) return <div className="error-container">{error}</div>;

  return (
    <div className="results-page-container">
      <div className="results-header-card">
        <h2>Kết quả bài thi</h2>
        <div className="score-display">
          Điểm số của bạn:
          <span className="final-score">
            {score !== undefined ? score : "N/A"} / {totalQuestions}
          </span>
        </div>
        <p>Dưới đây là chi tiết các câu trả lời của bạn.</p>
        <button className="back-home-button" onClick={() => navigate("/")}>
          Quay về trang chủ
        </button>
      </div>

      <div className="results-list">
        {results.map((q, index) => (
          <ResultQuestion
            key={q.question_id || index} // Sử dụng index nếu question_id bị thiếu
            question={q}
            index={index}
          />
        ))}
      </div>
    </div>
  );
}

export default ExamResultsPage;
