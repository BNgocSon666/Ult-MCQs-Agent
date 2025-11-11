import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css'; // Chúng ta sẽ tạo file CSS này ở dưới

// Bạn có thể import các icon từ react-icons nếu muốn
// import { FaFileUpload, FaBrain, FaShareAlt, FaFilePdf, FaMicrophone } from 'react-icons/fa';

function HomePage() {
  return (
    <div className="homepage-container">
      
      {/* === 1. Navbar === */}
      <nav className="homepage-navbar">
        <div className="nav-logo">
          {/* Sử dụng logo2.png từ thư mục /public/ */}
          <img src="/logo2.png" alt="Logo" className="logo-image"/>
          <span>Ultimate MCQs</span>
        </div>
        <div className="nav-actions">
          <Link to="/guide" className="nav-button guide">Hướng dẫn</Link>
          <Link to="/login" className="nav-button login">Đăng nhập</Link>
          <Link to="/register" className="nav-button register">Đăng ký</Link>
        </div>
      </nav>

      {/* === 2. Hero Section === */}
      <header className="hero-section">
        <div className="hero-logo">
          <img src="/logo2.png" alt="Logo" className="hero-logo-image" height={500} width={700}/>
        </div>
        <h1>Tạo Câu hỏi Trắc nghiệm Tức thì</h1>
        <h2>Biến tài liệu PDF, DOCX và cả file Ghi âm thành các bộ đề thi hoàn chỉnh chỉ trong vài giây.</h2>
        <p>Sử dụng sức mạnh của AI để tự động hóa việc soạn đề, đánh giá chất lượng và quản lý thư viện câu hỏi của bạn.</p>
        <Link to="/register" className="hero-cta-button">
          Bắt đầu miễn phí
        </Link>
      </header>

      {/* === 3. "How it Works" Section === */}
      <section className="how-it-works">
        <h3>Chỉ với 3 bước đơn giản</h3>
        <div className="steps-container">
          <div className="step-card">
            {/* <FaFileUpload size={40} /> */}
            <strong>1. Tải lên</strong>
            <p>Tải lên file PDF, DOCX, TXT hoặc file âm thanh (MP3, WAV, M4A).</p>
          </div>
          <div className="step-card">
            {/* <FaBrain size={40} /> */}
            <strong>2. AI Phân tích</strong>
            <p>AI tự động phân tích, tóm tắt, tạo câu hỏi và tự chấm điểm chất lượng từng câu.</p>
          </div>
          <div className="step-card">
            {/* <FaShareAlt size={40} /> */}
            <strong>3. Sử dụng & Chia sẻ</strong>
            <p>Chỉnh sửa, lưu vào thư viện, tạo đề thi và chia sẻ công khai cho người khác làm bài.</p>
          </div>
        </div>
      </section>

      {/* === 4. Features Section === */}
      <section className="features-section">
        <h3>Tính năng vượt trội</h3>
        <div className="features-grid">
          <div className="feature-card">
            {/* <FaMicrophone size={30} /> */}
            <strong>Từ Âm thanh sang Câu hỏi</strong>
            <p>Một tính năng độc đáo cho phép bạn biến các bài giảng, cuộc họp (MP3, WAV) thành bộ câu hỏi ôn tập.</p>
          </div>
          <div className="feature-card">
            {/* <FaBrain size={30} /> */}
            <strong>Đánh giá Chất lượng bằng AI</strong>
            <p>Mỗi câu hỏi được AI tự chấm điểm (Accuracy, Clarity...) giúp bạn biết câu nào tốt nhất.</p>
          </div>
          <div className="feature-card">
            {/* <FaShareAlt size={30} /> */}
            <strong>Xây dựng & Chia sẻ Đề thi</strong>
            <p>Tổ chức câu hỏi thành các đề thi hoàn chỉnh và chia sẻ qua một link công khai cho mọi người.</p>
          </div>
          <div className="feature-card">
            {/* <FaFilePdf size={30} /> */}
            <strong>Xuất file PDF chuyên nghiệp</strong>
            <p>Lưu trữ đề thi và đáp án của bạn dưới dạng file PDF có thể in ấn ngay lập tức.</p>
          </div>
        </div>
      </section>

      {/* === 5. Final Call to Action (CTA) === */}
      <section className="final-cta">
        <h2>Bắt đầu tiết kiệm thời gian ngay hôm nay.</h2>
        <p>Tham gia cùng hàng ngàn giáo viên, nhà quản lý đào tạo và sinh viên đang tự động hóa công việc của họ.</p>
        <Link to="/register" className="hero-cta-button">
          Đăng ký tài khoản miễn phí
        </Link>
      </section>

      {/* === 6. Footer === */}
      <footer className="homepage-footer">
        <p>© {new Date().getFullYear()} Ultimate MCQs Agent. Phát triển bởi Hội người không biết gì.</p>
      </footer>

    </div>
  );
}

export default HomePage;