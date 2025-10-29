-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Oct 29, 2025 at 10:21 AM
-- Server version: 10.11.14-MariaDB-cll-lve-log
-- PHP Version: 8.4.13

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `spdhlmjn_mcqs`
--

DELIMITER $$
--
-- Procedures
--
$$

$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `ExamQuestions`
--

CREATE TABLE `ExamQuestions` (
  `exam_question_id` int(11) NOT NULL,
  `exam_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `order_index` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

--
-- Dumping data for table `ExamQuestions`
--

INSERT INTO `ExamQuestions` (`exam_question_id`, `exam_id`, `question_id`, `order_index`) VALUES
(1, 1, 55, 0),
(2, 1, 56, 0),
(3, 1, 61, 0),
(4, 3, 64, 0),
(5, 3, 65, 0),
(6, 3, 66, 0);

-- --------------------------------------------------------

--
-- Table structure for table `Exams`
--

CREATE TABLE `Exams` (
  `exam_id` int(11) NOT NULL,
  `owner_id` int(11) NOT NULL,
  `title` varchar(500) NOT NULL,
  `description` longtext DEFAULT NULL,
  `share_token` varchar(50) NOT NULL,
  `is_public` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `Exams`
--

INSERT INTO `Exams` (`exam_id`, `owner_id`, `title`, `description`, `share_token`, `is_public`, `created_at`) VALUES
(1, 3, 'test', 'test', '', 0, '2025-10-28 14:50:15'),
(3, 4, 'nhat', 'nhat', '3475bd073c471301', 0, '2025-10-29 00:24:43');

-- --------------------------------------------------------

--
-- Table structure for table `ExamSessions`
--

CREATE TABLE `ExamSessions` (
  `session_id` int(11) NOT NULL,
  `exam_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `guest_name` varchar(255) DEFAULT NULL,
  `start_time` datetime DEFAULT current_timestamp(),
  `end_time` datetime DEFAULT NULL,
  `total_score` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

--
-- Dumping data for table `ExamSessions`
--

INSERT INTO `ExamSessions` (`session_id`, `exam_id`, `user_id`, `guest_name`, `start_time`, `end_time`, `total_score`) VALUES
(1, 1, 3, 'Thuan', '2025-10-28 15:15:04', '2025-10-28 15:16:55', 0),
(2, 3, 4, 'nhat', '2025-10-29 00:26:38', '2025-10-29 00:28:24', 3),
(3, 3, 2, 'wtf', '2025-10-29 09:11:22', '2025-10-29 10:00:13', 0),
(4, 3, 2, 'wtf', '2025-10-29 09:40:10', NULL, NULL),
(5, 3, 2, 'lzgiangtruong', '2025-10-29 09:42:03', '2025-10-29 10:00:57', 0);

-- --------------------------------------------------------

--
-- Table structure for table `Files`
--

CREATE TABLE `Files` (
  `file_id` int(11) NOT NULL,
  `uploader_id` int(11) NOT NULL,
  `filename` varchar(500) NOT NULL,
  `file_type` varchar(50) NOT NULL,
  `uploaded_at` datetime DEFAULT current_timestamp(),
  `storage_path` varchar(500) DEFAULT NULL,
  `raw_text` longtext DEFAULT NULL,
  `summary` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

--
-- Dumping data for table `Files`
--

INSERT INTO `Files` (`file_id`, `uploader_id`, `filename`, `file_type`, `uploaded_at`, `storage_path`, `raw_text`, `summary`) VALUES
(8, 3, 'PTUD_M4_Bi?u m?u thuy?t minh ?? tài.pdf', 'PDF', '2025-10-24 14:32:17', NULL, '??ng ký thuy?t minh ?? tài H?c ph?n phát tri?n ?ng d?ng — O0O — 1.? Thông tin sinh viên MSSV (??i di?n): 122001281 H? và tên (??i di?n): Bùi Ng?c S?n Danh sách sinh viên trong nhóm: STT MSSV H? và tên Ký tên 01 122000860 Tr?n Tr?ng Thu?n 02 122001281 Bùi Ng?c S?n 2.? Thông tin giáo viên h??ng d?n H? và tên GV: Nguy?n Minh S?n ?i?n tho?i: 0946 734 111 Email: nmson@lhu.edu.vn 3.? Tên d? án/ ?? tài (d? ki?n) th?c hi?n trong h?c ph?n ?ng d?ng Web t? ??ng t?o câu h?i tr?c nghi?m t? tài li?u (giáo trình, ghi âm, bài báo) 4.? Tóm t?t ?? tài ?? tài “H? th?ng sinh câu h?i tr?c nghi?m” nh?m xây d?ng m?t công c? t? ??ng có kh? n?ng tóm t?t n?i dung t? tài li?u, bài gi?ng ho?c ghi âm, sau ?ó sinh ra các câu h?i tr?c nghi?m g?m câu h?i, ?áp án ?úng và các ?áp án nhi?u. H? th?ng ???c ?ng d?ng trong giáo d?c và doanh nghi?p, giúp gi?ng viên, qu?n lý ho?c ng??i ?ào t?o nhanh chóng ki?m tra m?c ?? hi?u c?a ng??i h?c ho?c nhân viên, ??ng th?i ti?t ki?m th?i gian so?n ??, nâng cao hi?u qu? ?ánh giá và ?ào t?o. 5.? M?c tiêu và k?t qu? mong ??i M?c tiêu c?a ?? tài: ?? Xây d?ng AI agent có kh? n?ng ??c – hi?u n?i dung t? file PDF, DOCX ho?c file âm thanh. ?? Sinh câu h?i tr?c nghi?m g?m câu h?i, ?áp án ?úng và ?áp án nhi?u. ?? ?ng d?ng ???c cho nhi?u l?nh v?c: giáo d?c, doanh nghi?p, ?ào t?o n?i b?, và nghiên c?u. ?? ?ng d?ng x? lý ngôn ng? t? nhiên (NLP) và Machine Learning ?? ??m b?o ch?t l??ng câu h?i. Tóm t?t và trích xu?t ý chính c?a tài li?u m?t cách t? nhiên. K?t qu? c?a ?? tài: ?? H? th?ng AI có kh? n?ng x? lý nhanh, chính xác và sinh câu h?i ch?t l??ng cao. ?? Web app thân thi?n cho phép ng??i dùng upload tài li?u ho?c ghi âm ?? sinh câu h?i t? ??ng. ?? L?u tr? và qu?n lý ngân hàng câu h?i ?? tái s? d?ng trong gi?ng d?y và ?ào t?o. ?? Nâng cao hi?u qu? h?c t?p và ?ào t?o, giúp ?ánh giá nhanh, khách quan và chính xác. H? th?ng cho phép ng??i dùng, ?? Gi?ng viên: t?o ?? nhanh, ti?t ki?m th?i gian, ?ánh giá m?c ?? ti?p thu c?a h?c sinh. ?? H?c sinh, sinh viên: ôn t?p, luy?n t?p và t? ki?m tra ki?n th?c. ?? Doanh nghi?p: ki?m tra m?c ?? hi?u c?a nhân viên sau các bu?i h?p ho?c ?ào t?o. ?? Qu?n lý ?ào t?o: theo dõi, t?ng h?p k?t qu? và c?i thi?n n?i dung gi?ng d?y. 6.? K? ho?ch th?c hi?n STT N?i dung th?c hi?n Th?i gian Ng??i th?c hi?n 01 Kh?o sát & phân tích yêu c?u: Tìm hi?u các h? th?ng AI t??ng t? (Gemini, ChatGPT, AutoQuiz AI); xác ??nh yêu c?u ??u vào (file PDF, DOCX, audio) và ??u ra (summary + MCQ JSON). 1 tu?n T? ngày 30/09 ??n ngày 7/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 02 Thi?t k? ki?n trúc t?ng th?: Lu?ng x? lý gi?a Web – Backend – Gemini API – DataBase; thi?t k? ERD, DFD và lu?ng d? li?u. 1 tu?n T? ngày 7/10 ??n ngày 14/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 03 Xây d?ng AI Agent tóm t?t n?i dung: Tích h?p Gemini API ?? tóm t?t v?n b?n ho?c file âm thanh. Chu?n hóa d? li?u ??u vào. 1 tu?n T? ngày 14/10 ??n ngày 21/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 04 Xây d?ng AI Agent sinh câu h?i: S? d?ng tóm t?t t? b??c tr??c ?? sinh câu h?i tr?c nghi?m. ??m b?o có 1 ?áp ?úng và 3 ?áp nhi?u; ??nh d?ng JSON chu?n. 1 tu?n T? ngày 21/10 ??n ngày 28/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 05 Xây d?ng h? th?ng qu?n lý câu h?i: Thêm, s?a, xóa, phân lo?i, export câu h?i; h? tr? ?a ng??i dùng. 1 tu?n T? ngày 28/10 ??n ngày 4/11 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 06 Phát tri?n giao di?n web & API: Xây d?ng giao di?n upload tài li?u, hi?n th? tóm t?t và câu h?i; k?t n?i FastAPI backend v?i DeepSeek; hoàn thi?n tr?i nghi?m ng??i dùng. 1 tu?n T? ngày 4/11 ??n ngày 11/11 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 07 Ki?m th?, t?i ?u & b?o m?t: ?ánh giá ch?t l??ng câu h?i, t?c ?? ph?n h?i API, x? lý t?p l?n, gi?i h?n request, ?n API key, b?o m?t d? li?u ng??i dùng. 1 tu?n T? ngày 11/11 ??n ngày 18/11 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 08 Hoàn thi?n và báo cáo: Vi?t báo cáo, làm slide thuy?t trình, demo 1 tu?n Tr?n Tr?ng Thu?n - Bùi Ng?c S?n h? th?ng AI quiz agent hoàn ch?nh. T? ngày 18/11 ??n ngày 25/11 ? ? ??ng Nai, Ngày 09 tháng 10 n?m 2025 GVHD? Sinh viên ??i di?n? ? (Ký tên và ghi rõ h? tên)? (Ký tên và ghi rõ h? tên) ? Nguy?n Minh S?n? Bùi Ng?c S?n', NULL),
(9, 3, 'PTUD_M4_Bi?u m?u thuy?t minh ?? tài.pdf', 'PDF', '2025-10-24 14:35:51', NULL, '??ng ký thuy?t minh ?? tài H?c ph?n phát tri?n ?ng d?ng — O0O — 1.? Thông tin sinh viên MSSV (??i di?n): 122001281 H? và tên (??i di?n): Bùi Ng?c S?n Danh sách sinh viên trong nhóm: STT MSSV H? và tên Ký tên 01 122000860 Tr?n Tr?ng Thu?n 02 122001281 Bùi Ng?c S?n 2.? Thông tin giáo viên h??ng d?n H? và tên GV: Nguy?n Minh S?n ?i?n tho?i: 0946 734 111 Email: nmson@lhu.edu.vn 3.? Tên d? án/ ?? tài (d? ki?n) th?c hi?n trong h?c ph?n ?ng d?ng Web t? ??ng t?o câu h?i tr?c nghi?m t? tài li?u (giáo trình, ghi âm, bài báo) 4.? Tóm t?t ?? tài ?? tài “H? th?ng sinh câu h?i tr?c nghi?m” nh?m xây d?ng m?t công c? t? ??ng có kh? n?ng tóm t?t n?i dung t? tài li?u, bài gi?ng ho?c ghi âm, sau ?ó sinh ra các câu h?i tr?c nghi?m g?m câu h?i, ?áp án ?úng và các ?áp án nhi?u. H? th?ng ???c ?ng d?ng trong giáo d?c và doanh nghi?p, giúp gi?ng viên, qu?n lý ho?c ng??i ?ào t?o nhanh chóng ki?m tra m?c ?? hi?u c?a ng??i h?c ho?c nhân viên, ??ng th?i ti?t ki?m th?i gian so?n ??, nâng cao hi?u qu? ?ánh giá và ?ào t?o. 5.? M?c tiêu và k?t qu? mong ??i M?c tiêu c?a ?? tài: ?? Xây d?ng AI agent có kh? n?ng ??c – hi?u n?i dung t? file PDF, DOCX ho?c file âm thanh. ?? Sinh câu h?i tr?c nghi?m g?m câu h?i, ?áp án ?úng và ?áp án nhi?u. ?? ?ng d?ng ???c cho nhi?u l?nh v?c: giáo d?c, doanh nghi?p, ?ào t?o n?i b?, và nghiên c?u. ?? ?ng d?ng x? lý ngôn ng? t? nhiên (NLP) và Machine Learning ?? ??m b?o ch?t l??ng câu h?i. Tóm t?t và trích xu?t ý chính c?a tài li?u m?t cách t? nhiên. K?t qu? c?a ?? tài: ?? H? th?ng AI có kh? n?ng x? lý nhanh, chính xác và sinh câu h?i ch?t l??ng cao. ?? Web app thân thi?n cho phép ng??i dùng upload tài li?u ho?c ghi âm ?? sinh câu h?i t? ??ng. ?? L?u tr? và qu?n lý ngân hàng câu h?i ?? tái s? d?ng trong gi?ng d?y và ?ào t?o. ?? Nâng cao hi?u qu? h?c t?p và ?ào t?o, giúp ?ánh giá nhanh, khách quan và chính xác. H? th?ng cho phép ng??i dùng, ?? Gi?ng viên: t?o ?? nhanh, ti?t ki?m th?i gian, ?ánh giá m?c ?? ti?p thu c?a h?c sinh. ?? H?c sinh, sinh viên: ôn t?p, luy?n t?p và t? ki?m tra ki?n th?c. ?? Doanh nghi?p: ki?m tra m?c ?? hi?u c?a nhân viên sau các bu?i h?p ho?c ?ào t?o. ?? Qu?n lý ?ào t?o: theo dõi, t?ng h?p k?t qu? và c?i thi?n n?i dung gi?ng d?y. 6.? K? ho?ch th?c hi?n STT N?i dung th?c hi?n Th?i gian Ng??i th?c hi?n 01 Kh?o sát & phân tích yêu c?u: Tìm hi?u các h? th?ng AI t??ng t? (Gemini, ChatGPT, AutoQuiz AI); xác ??nh yêu c?u ??u vào (file PDF, DOCX, audio) và ??u ra (summary + MCQ JSON). 1 tu?n T? ngày 30/09 ??n ngày 7/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 02 Thi?t k? ki?n trúc t?ng th?: Lu?ng x? lý gi?a Web – Backend – Gemini API – DataBase; thi?t k? ERD, DFD và lu?ng d? li?u. 1 tu?n T? ngày 7/10 ??n ngày 14/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 03 Xây d?ng AI Agent tóm t?t n?i dung: Tích h?p Gemini API ?? tóm t?t v?n b?n ho?c file âm thanh. Chu?n hóa d? li?u ??u vào. 1 tu?n T? ngày 14/10 ??n ngày 21/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 04 Xây d?ng AI Agent sinh câu h?i: S? d?ng tóm t?t t? b??c tr??c ?? sinh câu h?i tr?c nghi?m. ??m b?o có 1 ?áp ?úng và 3 ?áp nhi?u; ??nh d?ng JSON chu?n. 1 tu?n T? ngày 21/10 ??n ngày 28/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 05 Xây d?ng h? th?ng qu?n lý câu h?i: Thêm, s?a, xóa, phân lo?i, export câu h?i; h? tr? ?a ng??i dùng. 1 tu?n T? ngày 28/10 ??n ngày 4/11 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 06 Phát tri?n giao di?n web & API: Xây d?ng giao di?n upload tài li?u, hi?n th? tóm t?t và câu h?i; k?t n?i FastAPI backend v?i DeepSeek; hoàn thi?n tr?i nghi?m ng??i dùng. 1 tu?n T? ngày 4/11 ??n ngày 11/11 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 07 Ki?m th?, t?i ?u & b?o m?t: ?ánh giá ch?t l??ng câu h?i, t?c ?? ph?n h?i API, x? lý t?p l?n, gi?i h?n request, ?n API key, b?o m?t d? li?u ng??i dùng. 1 tu?n T? ngày 11/11 ??n ngày 18/11 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 08 Hoàn thi?n và báo cáo: Vi?t báo cáo, làm slide thuy?t trình, demo 1 tu?n Tr?n Tr?ng Thu?n - Bùi Ng?c S?n h? th?ng AI quiz agent hoàn ch?nh. T? ngày 18/11 ??n ngày 25/11 ? ? ??ng Nai, Ngày 09 tháng 10 n?m 2025 GVHD? Sinh viên ??i di?n? ? (Ký tên và ghi rõ h? tên)? (Ký tên và ghi rõ h? tên) ? Nguy?n Minh S?n? Bùi Ng?c S?n', NULL),
(10, 3, 'PTUD_M4_Bi?u m?u thuy?t minh ?? tài.pdf', 'PDF', '2025-10-24 14:38:52', NULL, '??ng ký thuy?t minh ?? tài H?c ph?n phát tri?n ?ng d?ng — O0O — 1.? Thông tin sinh viên MSSV (??i di?n): 122001281 H? và tên (??i di?n): Bùi Ng?c S?n Danh sách sinh viên trong nhóm: STT MSSV H? và tên Ký tên 01 122000860 Tr?n Tr?ng Thu?n 02 122001281 Bùi Ng?c S?n 2.? Thông tin giáo viên h??ng d?n H? và tên GV: Nguy?n Minh S?n ?i?n tho?i: 0946 734 111 Email: nmson@lhu.edu.vn 3.? Tên d? án/ ?? tài (d? ki?n) th?c hi?n trong h?c ph?n ?ng d?ng Web t? ??ng t?o câu h?i tr?c nghi?m t? tài li?u (giáo trình, ghi âm, bài báo) 4.? Tóm t?t ?? tài ?? tài “H? th?ng sinh câu h?i tr?c nghi?m” nh?m xây d?ng m?t công c? t? ??ng có kh? n?ng tóm t?t n?i dung t? tài li?u, bài gi?ng ho?c ghi âm, sau ?ó sinh ra các câu h?i tr?c nghi?m g?m câu h?i, ?áp án ?úng và các ?áp án nhi?u. H? th?ng ???c ?ng d?ng trong giáo d?c và doanh nghi?p, giúp gi?ng viên, qu?n lý ho?c ng??i ?ào t?o nhanh chóng ki?m tra m?c ?? hi?u c?a ng??i h?c ho?c nhân viên, ??ng th?i ti?t ki?m th?i gian so?n ??, nâng cao hi?u qu? ?ánh giá và ?ào t?o. 5.? M?c tiêu và k?t qu? mong ??i M?c tiêu c?a ?? tài: ?? Xây d?ng AI agent có kh? n?ng ??c – hi?u n?i dung t? file PDF, DOCX ho?c file âm thanh. ?? Sinh câu h?i tr?c nghi?m g?m câu h?i, ?áp án ?úng và ?áp án nhi?u. ?? ?ng d?ng ???c cho nhi?u l?nh v?c: giáo d?c, doanh nghi?p, ?ào t?o n?i b?, và nghiên c?u. ?? ?ng d?ng x? lý ngôn ng? t? nhiên (NLP) và Machine Learning ?? ??m b?o ch?t l??ng câu h?i. Tóm t?t và trích xu?t ý chính c?a tài li?u m?t cách t? nhiên. K?t qu? c?a ?? tài: ?? H? th?ng AI có kh? n?ng x? lý nhanh, chính xác và sinh câu h?i ch?t l??ng cao. ?? Web app thân thi?n cho phép ng??i dùng upload tài li?u ho?c ghi âm ?? sinh câu h?i t? ??ng. ?? L?u tr? và qu?n lý ngân hàng câu h?i ?? tái s? d?ng trong gi?ng d?y và ?ào t?o. ?? Nâng cao hi?u qu? h?c t?p và ?ào t?o, giúp ?ánh giá nhanh, khách quan và chính xác. H? th?ng cho phép ng??i dùng, ?? Gi?ng viên: t?o ?? nhanh, ti?t ki?m th?i gian, ?ánh giá m?c ?? ti?p thu c?a h?c sinh. ?? H?c sinh, sinh viên: ôn t?p, luy?n t?p và t? ki?m tra ki?n th?c. ?? Doanh nghi?p: ki?m tra m?c ?? hi?u c?a nhân viên sau các bu?i h?p ho?c ?ào t?o. ?? Qu?n lý ?ào t?o: theo dõi, t?ng h?p k?t qu? và c?i thi?n n?i dung gi?ng d?y. 6.? K? ho?ch th?c hi?n STT N?i dung th?c hi?n Th?i gian Ng??i th?c hi?n 01 Kh?o sát & phân tích yêu c?u: Tìm hi?u các h? th?ng AI t??ng t? (Gemini, ChatGPT, AutoQuiz AI); xác ??nh yêu c?u ??u vào (file PDF, DOCX, audio) và ??u ra (summary + MCQ JSON). 1 tu?n T? ngày 30/09 ??n ngày 7/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 02 Thi?t k? ki?n trúc t?ng th?: Lu?ng x? lý gi?a Web – Backend – Gemini API – DataBase; thi?t k? ERD, DFD và lu?ng d? li?u. 1 tu?n T? ngày 7/10 ??n ngày 14/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 03 Xây d?ng AI Agent tóm t?t n?i dung: Tích h?p Gemini API ?? tóm t?t v?n b?n ho?c file âm thanh. Chu?n hóa d? li?u ??u vào. 1 tu?n T? ngày 14/10 ??n ngày 21/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 04 Xây d?ng AI Agent sinh câu h?i: S? d?ng tóm t?t t? b??c tr??c ?? sinh câu h?i tr?c nghi?m. ??m b?o có 1 ?áp ?úng và 3 ?áp nhi?u; ??nh d?ng JSON chu?n. 1 tu?n T? ngày 21/10 ??n ngày 28/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 05 Xây d?ng h? th?ng qu?n lý câu h?i: Thêm, s?a, xóa, phân lo?i, export câu h?i; h? tr? ?a ng??i dùng. 1 tu?n T? ngày 28/10 ??n ngày 4/11 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 06 Phát tri?n giao di?n web & API: Xây d?ng giao di?n upload tài li?u, hi?n th? tóm t?t và câu h?i; k?t n?i FastAPI backend v?i DeepSeek; hoàn thi?n tr?i nghi?m ng??i dùng. 1 tu?n T? ngày 4/11 ??n ngày 11/11 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 07 Ki?m th?, t?i ?u & b?o m?t: ?ánh giá ch?t l??ng câu h?i, t?c ?? ph?n h?i API, x? lý t?p l?n, gi?i h?n request, ?n API key, b?o m?t d? li?u ng??i dùng. 1 tu?n T? ngày 11/11 ??n ngày 18/11 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 08 Hoàn thi?n và báo cáo: Vi?t báo cáo, làm slide thuy?t trình, demo 1 tu?n Tr?n Tr?ng Thu?n - Bùi Ng?c S?n h? th?ng AI quiz agent hoàn ch?nh. T? ngày 18/11 ??n ngày 25/11 ? ? ??ng Nai, Ngày 09 tháng 10 n?m 2025 GVHD? Sinh viên ??i di?n? ? (Ký tên và ghi rõ h? tên)? (Ký tên và ghi rõ h? tên) ? Nguy?n Minh S?n? Bùi Ng?c S?n', NULL),
(11, 3, 'PTUD_M4_Bi?u m?u thuy?t minh ?? tài.pdf', 'PDF', '2025-10-24 14:51:15', NULL, '??ng ký thuy?t minh ?? tài H?c ph?n phát tri?n ?ng d?ng — O0O — 1.? Thông tin sinh viên MSSV (??i di?n): 122001281 H? và tên (??i di?n): Bùi Ng?c S?n Danh sách sinh viên trong nhóm: STT MSSV H? và tên Ký tên 01 122000860 Tr?n Tr?ng Thu?n 02 122001281 Bùi Ng?c S?n 2.? Thông tin giáo viên h??ng d?n H? và tên GV: Nguy?n Minh S?n ?i?n tho?i: 0946 734 111 Email: nmson@lhu.edu.vn 3.? Tên d? án/ ?? tài (d? ki?n) th?c hi?n trong h?c ph?n ?ng d?ng Web t? ??ng t?o câu h?i tr?c nghi?m t? tài li?u (giáo trình, ghi âm, bài báo) 4.? Tóm t?t ?? tài ?? tài “H? th?ng sinh câu h?i tr?c nghi?m” nh?m xây d?ng m?t công c? t? ??ng có kh? n?ng tóm t?t n?i dung t? tài li?u, bài gi?ng ho?c ghi âm, sau ?ó sinh ra các câu h?i tr?c nghi?m g?m câu h?i, ?áp án ?úng và các ?áp án nhi?u. H? th?ng ???c ?ng d?ng trong giáo d?c và doanh nghi?p, giúp gi?ng viên, qu?n lý ho?c ng??i ?ào t?o nhanh chóng ki?m tra m?c ?? hi?u c?a ng??i h?c ho?c nhân viên, ??ng th?i ti?t ki?m th?i gian so?n ??, nâng cao hi?u qu? ?ánh giá và ?ào t?o. 5.? M?c tiêu và k?t qu? mong ??i M?c tiêu c?a ?? tài: ?? Xây d?ng AI agent có kh? n?ng ??c – hi?u n?i dung t? file PDF, DOCX ho?c file âm thanh. ?? Sinh câu h?i tr?c nghi?m g?m câu h?i, ?áp án ?úng và ?áp án nhi?u. ?? ?ng d?ng ???c cho nhi?u l?nh v?c: giáo d?c, doanh nghi?p, ?ào t?o n?i b?, và nghiên c?u. ?? ?ng d?ng x? lý ngôn ng? t? nhiên (NLP) và Machine Learning ?? ??m b?o ch?t l??ng câu h?i. Tóm t?t và trích xu?t ý chính c?a tài li?u m?t cách t? nhiên. K?t qu? c?a ?? tài: ?? H? th?ng AI có kh? n?ng x? lý nhanh, chính xác và sinh câu h?i ch?t l??ng cao. ?? Web app thân thi?n cho phép ng??i dùng upload tài li?u ho?c ghi âm ?? sinh câu h?i t? ??ng. ?? L?u tr? và qu?n lý ngân hàng câu h?i ?? tái s? d?ng trong gi?ng d?y và ?ào t?o. ?? Nâng cao hi?u qu? h?c t?p và ?ào t?o, giúp ?ánh giá nhanh, khách quan và chính xác. H? th?ng cho phép ng??i dùng, ?? Gi?ng viên: t?o ?? nhanh, ti?t ki?m th?i gian, ?ánh giá m?c ?? ti?p thu c?a h?c sinh. ?? H?c sinh, sinh viên: ôn t?p, luy?n t?p và t? ki?m tra ki?n th?c. ?? Doanh nghi?p: ki?m tra m?c ?? hi?u c?a nhân viên sau các bu?i h?p ho?c ?ào t?o. ?? Qu?n lý ?ào t?o: theo dõi, t?ng h?p k?t qu? và c?i thi?n n?i dung gi?ng d?y. 6.? K? ho?ch th?c hi?n STT N?i dung th?c hi?n Th?i gian Ng??i th?c hi?n 01 Kh?o sát & phân tích yêu c?u: Tìm hi?u các h? th?ng AI t??ng t? (Gemini, ChatGPT, AutoQuiz AI); xác ??nh yêu c?u ??u vào (file PDF, DOCX, audio) và ??u ra (summary + MCQ JSON). 1 tu?n T? ngày 30/09 ??n ngày 7/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 02 Thi?t k? ki?n trúc t?ng th?: Lu?ng x? lý gi?a Web – Backend – Gemini API – DataBase; thi?t k? ERD, DFD và lu?ng d? li?u. 1 tu?n T? ngày 7/10 ??n ngày 14/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 03 Xây d?ng AI Agent tóm t?t n?i dung: Tích h?p Gemini API ?? tóm t?t v?n b?n ho?c file âm thanh. Chu?n hóa d? li?u ??u vào. 1 tu?n T? ngày 14/10 ??n ngày 21/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 04 Xây d?ng AI Agent sinh câu h?i: S? d?ng tóm t?t t? b??c tr??c ?? sinh câu h?i tr?c nghi?m. ??m b?o có 1 ?áp ?úng và 3 ?áp nhi?u; ??nh d?ng JSON chu?n. 1 tu?n T? ngày 21/10 ??n ngày 28/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 05 Xây d?ng h? th?ng qu?n lý câu h?i: Thêm, s?a, xóa, phân lo?i, export câu h?i; h? tr? ?a ng??i dùng. 1 tu?n T? ngày 28/10 ??n ngày 4/11 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 06 Phát tri?n giao di?n web & API: Xây d?ng giao di?n upload tài li?u, hi?n th? tóm t?t và câu h?i; k?t n?i FastAPI backend v?i DeepSeek; hoàn thi?n tr?i nghi?m ng??i dùng. 1 tu?n T? ngày 4/11 ??n ngày 11/11 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 07 Ki?m th?, t?i ?u & b?o m?t: ?ánh giá ch?t l??ng câu h?i, t?c ?? ph?n h?i API, x? lý t?p l?n, gi?i h?n request, ?n API key, b?o m?t d? li?u ng??i dùng. 1 tu?n T? ngày 11/11 ??n ngày 18/11 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 08 Hoàn thi?n và báo cáo: Vi?t báo cáo, làm slide thuy?t trình, demo 1 tu?n Tr?n Tr?ng Thu?n - Bùi Ng?c S?n h? th?ng AI quiz agent hoàn ch?nh. T? ngày 18/11 ??n ngày 25/11 ? ? ??ng Nai, Ngày 09 tháng 10 n?m 2025 GVHD? Sinh viên ??i di?n? ? (Ký tên và ghi rõ h? tên)? (Ký tên và ghi rõ h? tên) ? Nguy?n Minh S?n? Bùi Ng?c S?n', NULL),
(12, 3, 'PTUD_M4_Bi?u m?u thuy?t minh ?? tài.pdf', 'PDF', '2025-10-24 15:01:57', NULL, '??ng ký thuy?t minh ?? tài H?c ph?n phát tri?n ?ng d?ng — O0O — 1.? Thông tin sinh viên MSSV (??i di?n): 122001281 H? và tên (??i di?n): Bùi Ng?c S?n Danh sách sinh viên trong nhóm: STT MSSV H? và tên Ký tên 01 122000860 Tr?n Tr?ng Thu?n 02 122001281 Bùi Ng?c S?n 2.? Thông tin giáo viên h??ng d?n H? và tên GV: Nguy?n Minh S?n ?i?n tho?i: 0946 734 111 Email: nmson@lhu.edu.vn 3.? Tên d? án/ ?? tài (d? ki?n) th?c hi?n trong h?c ph?n ?ng d?ng Web t? ??ng t?o câu h?i tr?c nghi?m t? tài li?u (giáo trình, ghi âm, bài báo) 4.? Tóm t?t ?? tài ?? tài “H? th?ng sinh câu h?i tr?c nghi?m” nh?m xây d?ng m?t công c? t? ??ng có kh? n?ng tóm t?t n?i dung t? tài li?u, bài gi?ng ho?c ghi âm, sau ?ó sinh ra các câu h?i tr?c nghi?m g?m câu h?i, ?áp án ?úng và các ?áp án nhi?u. H? th?ng ???c ?ng d?ng trong giáo d?c và doanh nghi?p, giúp gi?ng viên, qu?n lý ho?c ng??i ?ào t?o nhanh chóng ki?m tra m?c ?? hi?u c?a ng??i h?c ho?c nhân viên, ??ng th?i ti?t ki?m th?i gian so?n ??, nâng cao hi?u qu? ?ánh giá và ?ào t?o. 5.? M?c tiêu và k?t qu? mong ??i M?c tiêu c?a ?? tài: ?? Xây d?ng AI agent có kh? n?ng ??c – hi?u n?i dung t? file PDF, DOCX ho?c file âm thanh. ?? Sinh câu h?i tr?c nghi?m g?m câu h?i, ?áp án ?úng và ?áp án nhi?u. ?? ?ng d?ng ???c cho nhi?u l?nh v?c: giáo d?c, doanh nghi?p, ?ào t?o n?i b?, và nghiên c?u. ?? ?ng d?ng x? lý ngôn ng? t? nhiên (NLP) và Machine Learning ?? ??m b?o ch?t l??ng câu h?i. Tóm t?t và trích xu?t ý chính c?a tài li?u m?t cách t? nhiên. K?t qu? c?a ?? tài: ?? H? th?ng AI có kh? n?ng x? lý nhanh, chính xác và sinh câu h?i ch?t l??ng cao. ?? Web app thân thi?n cho phép ng??i dùng upload tài li?u ho?c ghi âm ?? sinh câu h?i t? ??ng. ?? L?u tr? và qu?n lý ngân hàng câu h?i ?? tái s? d?ng trong gi?ng d?y và ?ào t?o. ?? Nâng cao hi?u qu? h?c t?p và ?ào t?o, giúp ?ánh giá nhanh, khách quan và chính xác. H? th?ng cho phép ng??i dùng, ?? Gi?ng viên: t?o ?? nhanh, ti?t ki?m th?i gian, ?ánh giá m?c ?? ti?p thu c?a h?c sinh. ?? H?c sinh, sinh viên: ôn t?p, luy?n t?p và t? ki?m tra ki?n th?c. ?? Doanh nghi?p: ki?m tra m?c ?? hi?u c?a nhân viên sau các bu?i h?p ho?c ?ào t?o. ?? Qu?n lý ?ào t?o: theo dõi, t?ng h?p k?t qu? và c?i thi?n n?i dung gi?ng d?y. 6.? K? ho?ch th?c hi?n STT N?i dung th?c hi?n Th?i gian Ng??i th?c hi?n 01 Kh?o sát & phân tích yêu c?u: Tìm hi?u các h? th?ng AI t??ng t? (Gemini, ChatGPT, AutoQuiz AI); xác ??nh yêu c?u ??u vào (file PDF, DOCX, audio) và ??u ra (summary + MCQ JSON). 1 tu?n T? ngày 30/09 ??n ngày 7/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 02 Thi?t k? ki?n trúc t?ng th?: Lu?ng x? lý gi?a Web – Backend – Gemini API – DataBase; thi?t k? ERD, DFD và lu?ng d? li?u. 1 tu?n T? ngày 7/10 ??n ngày 14/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 03 Xây d?ng AI Agent tóm t?t n?i dung: Tích h?p Gemini API ?? tóm t?t v?n b?n ho?c file âm thanh. Chu?n hóa d? li?u ??u vào. 1 tu?n T? ngày 14/10 ??n ngày 21/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 04 Xây d?ng AI Agent sinh câu h?i: S? d?ng tóm t?t t? b??c tr??c ?? sinh câu h?i tr?c nghi?m. ??m b?o có 1 ?áp ?úng và 3 ?áp nhi?u; ??nh d?ng JSON chu?n. 1 tu?n T? ngày 21/10 ??n ngày 28/10 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 05 Xây d?ng h? th?ng qu?n lý câu h?i: Thêm, s?a, xóa, phân lo?i, export câu h?i; h? tr? ?a ng??i dùng. 1 tu?n T? ngày 28/10 ??n ngày 4/11 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 06 Phát tri?n giao di?n web & API: Xây d?ng giao di?n upload tài li?u, hi?n th? tóm t?t và câu h?i; k?t n?i FastAPI backend v?i DeepSeek; hoàn thi?n tr?i nghi?m ng??i dùng. 1 tu?n T? ngày 4/11 ??n ngày 11/11 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 07 Ki?m th?, t?i ?u & b?o m?t: ?ánh giá ch?t l??ng câu h?i, t?c ?? ph?n h?i API, x? lý t?p l?n, gi?i h?n request, ?n API key, b?o m?t d? li?u ng??i dùng. 1 tu?n T? ngày 11/11 ??n ngày 18/11 Tr?n Tr?ng Thu?n - Bùi Ng?c S?n 08 Hoàn thi?n và báo cáo: Vi?t báo cáo, làm slide thuy?t trình, demo 1 tu?n Tr?n Tr?ng Thu?n - Bùi Ng?c S?n h? th?ng AI quiz agent hoàn ch?nh. T? ngày 18/11 ??n ngày 25/11 ? ? ??ng Nai, Ngày 09 tháng 10 n?m 2025 GVHD? Sinh viên ??i di?n? ? (Ký tên và ghi rõ h? tên)? (Ký tên và ghi rõ h? tên) ? Nguy?n Minh S?n? Bùi Ng?c S?n', NULL),
(23, 2, 'procedure.txt', 'TXT', '2025-10-24 16:05:11', NULL, 'DELIMITER $$ CREATE PROCEDURE sp_SaveQuestion ( IN p_source_file_id INT, IN p_creator_id INT, IN p_question_text TEXT, IN p_options_json JSON, IN p_answer_letter CHAR(1), IN p_status VARCHAR(50) ) BEGIN INSERT INTO Questions (source_file_id, creator_id, question_text, options, answer_letter, status, created_at) VALUES (p_source_file_id, p_creator_id, p_question_text, p_options_json, p_answer_letter, p_status, NOW()); END$$ DELIMITER ; DELIMITER $$ CREATE PROCEDURE sp_SaveFile ( IN p_uploader_id INT, IN p_filename VARCHAR(255), IN p_file_type VARCHAR(50), IN p_storage_path VARCHAR(255), IN p_raw_text LONGTEXT, IN p_summary LONGTEXT ) BEGIN INSERT INTO Files (uploader_id, filename, file_type, uploaded_at, storage_path, raw_text, summary) VALUES (p_uploader_id, p_filename, p_file_type, NOW(), p_storage_path, p_raw_text, p_summary); SELECT LAST_INSERT_ID() AS file_id; END$$ DELIMITER ;', NULL),
(24, 2, 'procedure.txt', 'TXT', '2025-10-24 16:09:41', NULL, 'DELIMITER $$ CREATE PROCEDURE sp_SaveQuestion ( IN p_source_file_id INT, IN p_creator_id INT, IN p_question_text TEXT, IN p_options_json JSON, IN p_answer_letter CHAR(1), IN p_status VARCHAR(50) ) BEGIN INSERT INTO Questions (source_file_id, creator_id, question_text, options, answer_letter, status, created_at) VALUES (p_source_file_id, p_creator_id, p_question_text, p_options_json, p_answer_letter, p_status, NOW()); END$$ DELIMITER ; DELIMITER $$ CREATE PROCEDURE sp_SaveFile ( IN p_uploader_id INT, IN p_filename VARCHAR(255), IN p_file_type VARCHAR(50), IN p_storage_path VARCHAR(255), IN p_raw_text LONGTEXT, IN p_summary LONGTEXT ) BEGIN INSERT INTO Files (uploader_id, filename, file_type, uploaded_at, storage_path, raw_text, summary) VALUES (p_uploader_id, p_filename, p_file_type, NOW(), p_storage_path, p_raw_text, p_summary); SELECT LAST_INSERT_ID() AS file_id; END$$ DELIMITER ;', NULL),
(25, 2, '122001281_BuiNgocSon_NguyenMinhSon.pdf', 'PDF', '2025-10-24 16:40:50', NULL, 'Đăng ký thuyết minh đề tài Học phần phát triển ứng dụng — O0O — 1.​ Thông tin sinh viên MSSV (Đại diện): 122001281 Họ và tên (Đại diện): Bùi Ngọc Sơn Danh sách sinh viên trong nhóm: STT MSSV Họ và tên Ký tên 01 122000860 Trần Trọng Thuận 02 122001281 Bùi Ngọc Sơn 2.​ Thông tin giáo viên hướng dẫn Họ và tên GV: Nguyễn Minh Sơn Điện thoại: 0946 734 111 Email: nmson@lhu.edu.vn 3.​ Tên dự án/ đề tài (dự kiến) thực hiện trong học phần Ứng dụng Web tự động tạo câu hỏi trắc nghiệm từ tài liệu (giáo trình, ghi âm, bài báo) 4.​ Tóm tắt đề tài Đề tài “Hệ thống sinh câu hỏi trắc nghiệm” nhằm xây dựng một công cụ tự động có khả năng tóm tắt nội dung từ tài liệu, bài giảng hoặc ghi âm, sau đó sinh ra các câu hỏi trắc nghiệm gồm câu hỏi, đáp án đúng và các đáp án nhiễu. Hệ thống được ứng dụng trong giáo dục và doanh nghiệp, giúp giảng viên, quản lý hoặc người đào tạo nhanh chóng kiểm tra mức độ hiểu của người học hoặc nhân viên, đồng thời tiết kiệm thời gian soạn đề, nâng cao hiệu quả đánh giá và đào tạo. 5.​ Mục tiêu và kết quả mong đợi Mục tiêu của đề tài: ●​ Xây dựng AI agent có khả năng đọc – hiểu nội dung từ file PDF, DOCX hoặc file âm thanh. ●​ Sinh câu hỏi trắc nghiệm gồm câu hỏi, đáp án đúng và đáp án nhiễu. ●​ Ứng dụng được cho nhiều lĩnh vực: giáo dục, doanh nghiệp, đào tạo nội bộ, và nghiên cứu. ●​ Ứng dụng xử lý ngôn ngữ tự nhiên (NLP) và Machine Learning để đảm bảo chất lượng câu hỏi. Tóm tắt và trích xuất ý chính của tài liệu một cách tự nhiên. Kết quả của đề tài: ●​ Hệ thống AI có khả năng xử lý nhanh, chính xác và sinh câu hỏi chất lượng cao. ●​ Web app thân thiện cho phép người dùng upload tài liệu hoặc ghi âm để sinh câu hỏi tự động. ●​ Lưu trữ và quản lý ngân hàng câu hỏi để tái sử dụng trong giảng dạy và đào tạo. ●​ Nâng cao hiệu quả học tập và đào tạo, giúp đánh giá nhanh, khách quan và chính xác. Hệ thống cho phép người dùng, ●​ Giảng viên: tạo đề nhanh, tiết kiệm thời gian, đánh giá mức độ tiếp thu của học sinh. ●​ Học sinh, sinh viên: ôn tập, luyện tập và tự kiểm tra kiến thức. ●​ Doanh nghiệp: kiểm tra mức độ hiểu của nhân viên sau các buổi họp hoặc đào tạo. ●​ Quản lý đào tạo: theo dõi, tổng hợp kết quả và cải thiện nội dung giảng dạy. 6.​ Kế hoạch thực hiện STT Nội dung thực hiện Thời gian Người thực hiện 01 Khảo sát & phân tích yêu cầu: Tìm hiểu các hệ thống AI tương tự (DeepSeek, ChatGPT, AutoQuiz AI); xác định yêu cầu đầu vào (file PDF, DOCX, audio) và đầu ra (summary + MCQ JSON). 1 tuần Từ ngày 30/09 đến ngày 7/10 Trần Trọng Thuận - Bùi Ngọc Sơn 02 Thiết kế kiến trúc tổng thể: Luồng xử lý giữa Web – Backend – DeepSeek API – DataBase; thiết kế ERD, DFD và luồng dữ liệu. 1 tuần Từ ngày 7/10 đến ngày 14/10 Trần Trọng Thuận - Bùi Ngọc Sơn 03 Xây dựng AI Agent tóm tắt nội dung: Tích hợp DeepSeek API để tóm tắt văn bản hoặc file âm thanh (qua Whisper / DeepSeek-Audio). Chuẩn hóa dữ liệu đầu vào. 1 tuần Từ ngày 14/10 đến ngày 21/10 Trần Trọng Thuận - Bùi Ngọc Sơn 04 Xây dựng AI Agent sinh câu hỏi: Sử dụng tóm tắt từ bước trước để sinh câu hỏi trắc nghiệm. Đảm bảo có 1 đáp đúng và 3 đáp nhiễu; định dạng JSON chuẩn. 1 tuần Từ ngày 21/10 đến ngày 28/10 Trần Trọng Thuận - Bùi Ngọc Sơn 05 Xây dựng hệ thống quản lý câu hỏi: Thêm, sửa, xóa, phân loại, export câu hỏi; hỗ trợ đa người dùng. 1 tuần Từ ngày 28/10 đến ngày 4/11 Trần Trọng Thuận - Bùi Ngọc Sơn 06 Phát triển giao diện web & API: Xây dựng giao diện upload tài liệu, hiển thị tóm tắt và câu hỏi; kết nối FastAPI backend với DeepSeek; hoàn thiện trải nghiệm người dùng. 1 tuần Từ ngày 4/11 đến ngày 11/11 Trần Trọng Thuận - Bùi Ngọc Sơn 07 Kiểm thử, tối ưu & bảo mật: Đánh giá chất lượng câu hỏi, tốc độ phản hồi API, xử lý tệp lớn, giới hạn request, ẩn API key, bảo mật dữ liệu người dùng. 1 tuần Từ ngày 11/11 đến ngày 18/11 Trần Trọng Thuận - Bùi Ngọc Sơn 08 Hoàn thiện và báo cáo: Viết báo cáo, làm slide thuyết trình, demo hệ thống AI quiz agent hoàn chỉnh. 1 tuần Từ ngày 18/11 đến ngày 25/11 Trần Trọng Thuận - Bùi Ngọc Sơn ​ ​ Đồng Nai, Ngày 09 tháng 10 năm 2025 GVHD​ Sinh viên đại diện​ ​ (Ký tên và ghi rõ họ tên)​ (Ký tên và ghi rõ họ tên) ​ ​ Bùi Ngọc Sơn', 'Ngôn ngữ của văn bản là **Tiếng Việt**.\n\nDưới đây là bản tóm tắt ngắn gọn, rõ ràng và đầy đủ:\n\nĐây là đề xuất dự án cho học phần Phát triển ứng dụng, tập trung vào việc xây dựng một **ứng dụng Web tự động tạo câu hỏi trắc nghiệm từ tài liệu** (PDF, DOCX, ghi âm). Hệ thống sử dụng AI để tóm tắt nội dung và sinh ra các câu hỏi trắc nghiệm hoàn chỉnh (gồm câu hỏi, đáp án đúng và đáp án nhiễu), ứng dụng công nghệ xử lý ngôn ngữ tự nhiên (NLP) và Machine Learning, tích hợp các API AI như DeepSeek. Mục tiêu chính là cung cấp công cụ hiệu quả cho giáo dục và doanh nghiệp, giúp giảng viên, quản lý hoặc người đào tạo tiết kiệm thời gian, nâng cao hiệu quả đánh giá và kiểm tra kiến thức của người học/nhân viên. Dự án kỳ vọng tạo ra một hệ thống AI nhanh, chính xác với giao diện web thân thiện, khả năng quản lý ngân hàng câu hỏi. Kế hoạch thực hiện kéo dài 8 tuần, bao gồm các giai đoạn từ khảo sát, thiết kế, xây dựng AI agent tóm tắt/sinh câu hỏi, phát triển giao diện, đến kiểm thử và báo cáo. Nhóm thực hiện gồm Bùi Ngọc Sơn và Trần Trọng Thuận, dưới sự hướng dẫn của GV Nguyễn Minh Sơn.'),
(26, 3, 'PTUD_M4_Biểu mẫu thuyết minh đề tài.pdf', 'PDF', '2025-10-24 18:21:59', NULL, 'Đăng ký thuyết minh đề tài Học phần phát triển ứng dụng — O0O — 1.​ Thông tin sinh viên MSSV (Đại diện): 122001281 Họ và tên (Đại diện): Bùi Ngọc Sơn Danh sách sinh viên trong nhóm: STT MSSV Họ và tên Ký tên 01 122000860 Trần Trọng Thuận 02 122001281 Bùi Ngọc Sơn 2.​ Thông tin giáo viên hướng dẫn Họ và tên GV: Nguyễn Minh Sơn Điện thoại: 0946 734 111 Email: nmson@lhu.edu.vn 3.​ Tên dự án/ đề tài (dự kiến) thực hiện trong học phần Ứng dụng Web tự động tạo câu hỏi trắc nghiệm từ tài liệu (giáo trình, ghi âm, bài báo) 4.​ Tóm tắt đề tài Đề tài “Hệ thống sinh câu hỏi trắc nghiệm” nhằm xây dựng một công cụ tự động có khả năng tóm tắt nội dung từ tài liệu, bài giảng hoặc ghi âm, sau đó sinh ra các câu hỏi trắc nghiệm gồm câu hỏi, đáp án đúng và các đáp án nhiễu. Hệ thống được ứng dụng trong giáo dục và doanh nghiệp, giúp giảng viên, quản lý hoặc người đào tạo nhanh chóng kiểm tra mức độ hiểu của người học hoặc nhân viên, đồng thời tiết kiệm thời gian soạn đề, nâng cao hiệu quả đánh giá và đào tạo. 5.​ Mục tiêu và kết quả mong đợi Mục tiêu của đề tài: ●​ Xây dựng AI agent có khả năng đọc – hiểu nội dung từ file PDF, DOCX hoặc file âm thanh. ●​ Sinh câu hỏi trắc nghiệm gồm câu hỏi, đáp án đúng và đáp án nhiễu. ●​ Ứng dụng được cho nhiều lĩnh vực: giáo dục, doanh nghiệp, đào tạo nội bộ, và nghiên cứu. ●​ Ứng dụng xử lý ngôn ngữ tự nhiên (NLP) và Machine Learning để đảm bảo chất lượng câu hỏi. Tóm tắt và trích xuất ý chính của tài liệu một cách tự nhiên. Kết quả của đề tài: ●​ Hệ thống AI có khả năng xử lý nhanh, chính xác và sinh câu hỏi chất lượng cao. ●​ Web app thân thiện cho phép người dùng upload tài liệu hoặc ghi âm để sinh câu hỏi tự động. ●​ Lưu trữ và quản lý ngân hàng câu hỏi để tái sử dụng trong giảng dạy và đào tạo. ●​ Nâng cao hiệu quả học tập và đào tạo, giúp đánh giá nhanh, khách quan và chính xác. Hệ thống cho phép người dùng, ●​ Giảng viên: tạo đề nhanh, tiết kiệm thời gian, đánh giá mức độ tiếp thu của học sinh. ●​ Học sinh, sinh viên: ôn tập, luyện tập và tự kiểm tra kiến thức. ●​ Doanh nghiệp: kiểm tra mức độ hiểu của nhân viên sau các buổi họp hoặc đào tạo. ●​ Quản lý đào tạo: theo dõi, tổng hợp kết quả và cải thiện nội dung giảng dạy. 6.​ Kế hoạch thực hiện STT Nội dung thực hiện Thời gian Người thực hiện 01 Khảo sát & phân tích yêu cầu: Tìm hiểu các hệ thống AI tương tự (Gemini, ChatGPT, AutoQuiz AI); xác định yêu cầu đầu vào (file PDF, DOCX, audio) và đầu ra (summary + MCQ JSON). 1 tuần Từ ngày 30/09 đến ngày 7/10 Trần Trọng Thuận - Bùi Ngọc Sơn 02 Thiết kế kiến trúc tổng thể: Luồng xử lý giữa Web – Backend – Gemini API – DataBase; thiết kế ERD, DFD và luồng dữ liệu. 1 tuần Từ ngày 7/10 đến ngày 14/10 Trần Trọng Thuận - Bùi Ngọc Sơn 03 Xây dựng AI Agent tóm tắt nội dung: Tích hợp Gemini API để tóm tắt văn bản hoặc file âm thanh. Chuẩn hóa dữ liệu đầu vào. 1 tuần Từ ngày 14/10 đến ngày 21/10 Trần Trọng Thuận - Bùi Ngọc Sơn 04 Xây dựng AI Agent sinh câu hỏi: Sử dụng tóm tắt từ bước trước để sinh câu hỏi trắc nghiệm. Đảm bảo có 1 đáp đúng và 3 đáp nhiễu; định dạng JSON chuẩn. 1 tuần Từ ngày 21/10 đến ngày 28/10 Trần Trọng Thuận - Bùi Ngọc Sơn 05 Xây dựng hệ thống quản lý câu hỏi: Thêm, sửa, xóa, phân loại, export câu hỏi; hỗ trợ đa người dùng. 1 tuần Từ ngày 28/10 đến ngày 4/11 Trần Trọng Thuận - Bùi Ngọc Sơn 06 Phát triển giao diện web & API: Xây dựng giao diện upload tài liệu, hiển thị tóm tắt và câu hỏi; kết nối FastAPI backend với DeepSeek; hoàn thiện trải nghiệm người dùng. 1 tuần Từ ngày 4/11 đến ngày 11/11 Trần Trọng Thuận - Bùi Ngọc Sơn 07 Kiểm thử, tối ưu & bảo mật: Đánh giá chất lượng câu hỏi, tốc độ phản hồi API, xử lý tệp lớn, giới hạn request, ẩn API key, bảo mật dữ liệu người dùng. 1 tuần Từ ngày 11/11 đến ngày 18/11 Trần Trọng Thuận - Bùi Ngọc Sơn 08 Hoàn thiện và báo cáo: Viết báo cáo, làm slide thuyết trình, demo 1 tuần Trần Trọng Thuận - Bùi Ngọc Sơn hệ thống AI quiz agent hoàn chỉnh. Từ ngày 18/11 đến ngày 25/11 ​ ​ Đồng Nai, Ngày 09 tháng 10 năm 2025 GVHD​ Sinh viên đại diện​ ​ (Ký tên và ghi rõ họ tên)​ (Ký tên và ghi rõ họ tên) ​ Nguyễn Minh Sơn​ Bùi Ngọc Sơn', NULL),
(27, 3, 'PTUD_M4_Biểu mẫu thuyết minh đề tài.pdf', 'PDF', '2025-10-28 09:55:55', NULL, 'Đăng ký thuyết minh đề tài Học phần phát triển ứng dụng — O0O — 1.​ Thông tin sinh viên MSSV (Đại diện): 122001281 Họ và tên (Đại diện): Bùi Ngọc Sơn Danh sách sinh viên trong nhóm: STT MSSV Họ và tên Ký tên 01 122000860 Trần Trọng Thuận 02 122001281 Bùi Ngọc Sơn 2.​ Thông tin giáo viên hướng dẫn Họ và tên GV: Nguyễn Minh Sơn Điện thoại: 0946 734 111 Email: nmson@lhu.edu.vn 3.​ Tên dự án/ đề tài (dự kiến) thực hiện trong học phần Ứng dụng Web tự động tạo câu hỏi trắc nghiệm từ tài liệu (giáo trình, ghi âm, bài báo) 4.​ Tóm tắt đề tài Đề tài “Hệ thống sinh câu hỏi trắc nghiệm” nhằm xây dựng một công cụ tự động có khả năng tóm tắt nội dung từ tài liệu, bài giảng hoặc ghi âm, sau đó sinh ra các câu hỏi trắc nghiệm gồm câu hỏi, đáp án đúng và các đáp án nhiễu. Hệ thống được ứng dụng trong giáo dục và doanh nghiệp, giúp giảng viên, quản lý hoặc người đào tạo nhanh chóng kiểm tra mức độ hiểu của người học hoặc nhân viên, đồng thời tiết kiệm thời gian soạn đề, nâng cao hiệu quả đánh giá và đào tạo. 5.​ Mục tiêu và kết quả mong đợi Mục tiêu của đề tài: ●​ Xây dựng AI agent có khả năng đọc – hiểu nội dung từ file PDF, DOCX hoặc file âm thanh. ●​ Sinh câu hỏi trắc nghiệm gồm câu hỏi, đáp án đúng và đáp án nhiễu. ●​ Ứng dụng được cho nhiều lĩnh vực: giáo dục, doanh nghiệp, đào tạo nội bộ, và nghiên cứu. ●​ Ứng dụng xử lý ngôn ngữ tự nhiên (NLP) và Machine Learning để đảm bảo chất lượng câu hỏi. Tóm tắt và trích xuất ý chính của tài liệu một cách tự nhiên. Kết quả của đề tài: ●​ Hệ thống AI có khả năng xử lý nhanh, chính xác và sinh câu hỏi chất lượng cao. ●​ Web app thân thiện cho phép người dùng upload tài liệu hoặc ghi âm để sinh câu hỏi tự động. ●​ Lưu trữ và quản lý ngân hàng câu hỏi để tái sử dụng trong giảng dạy và đào tạo. ●​ Nâng cao hiệu quả học tập và đào tạo, giúp đánh giá nhanh, khách quan và chính xác. Hệ thống cho phép người dùng, ●​ Giảng viên: tạo đề nhanh, tiết kiệm thời gian, đánh giá mức độ tiếp thu của học sinh. ●​ Học sinh, sinh viên: ôn tập, luyện tập và tự kiểm tra kiến thức. ●​ Doanh nghiệp: kiểm tra mức độ hiểu của nhân viên sau các buổi họp hoặc đào tạo. ●​ Quản lý đào tạo: theo dõi, tổng hợp kết quả và cải thiện nội dung giảng dạy. 6.​ Kế hoạch thực hiện STT Nội dung thực hiện Thời gian Người thực hiện 01 Khảo sát & phân tích yêu cầu: Tìm hiểu các hệ thống AI tương tự (Gemini, ChatGPT, AutoQuiz AI); xác định yêu cầu đầu vào (file PDF, DOCX, audio) và đầu ra (summary + MCQ JSON). 1 tuần Từ ngày 30/09 đến ngày 7/10 Trần Trọng Thuận - Bùi Ngọc Sơn 02 Thiết kế kiến trúc tổng thể: Luồng xử lý giữa Web – Backend – Gemini API – DataBase; thiết kế ERD, DFD và luồng dữ liệu. 1 tuần Từ ngày 7/10 đến ngày 14/10 Trần Trọng Thuận - Bùi Ngọc Sơn 03 Xây dựng AI Agent tóm tắt nội dung: Tích hợp Gemini API để tóm tắt văn bản hoặc file âm thanh. Chuẩn hóa dữ liệu đầu vào. 1 tuần Từ ngày 14/10 đến ngày 21/10 Trần Trọng Thuận - Bùi Ngọc Sơn 04 Xây dựng AI Agent sinh câu hỏi: Sử dụng tóm tắt từ bước trước để sinh câu hỏi trắc nghiệm. Đảm bảo có 1 đáp đúng và 3 đáp nhiễu; định dạng JSON chuẩn. 1 tuần Từ ngày 21/10 đến ngày 28/10 Trần Trọng Thuận - Bùi Ngọc Sơn 05 Xây dựng hệ thống quản lý câu hỏi: Thêm, sửa, xóa, phân loại, export câu hỏi; hỗ trợ đa người dùng. 1 tuần Từ ngày 28/10 đến ngày 4/11 Trần Trọng Thuận - Bùi Ngọc Sơn 06 Phát triển giao diện web & API: Xây dựng giao diện upload tài liệu, hiển thị tóm tắt và câu hỏi; kết nối FastAPI backend với DeepSeek; hoàn thiện trải nghiệm người dùng. 1 tuần Từ ngày 4/11 đến ngày 11/11 Trần Trọng Thuận - Bùi Ngọc Sơn 07 Kiểm thử, tối ưu & bảo mật: Đánh giá chất lượng câu hỏi, tốc độ phản hồi API, xử lý tệp lớn, giới hạn request, ẩn API key, bảo mật dữ liệu người dùng. 1 tuần Từ ngày 11/11 đến ngày 18/11 Trần Trọng Thuận - Bùi Ngọc Sơn 08 Hoàn thiện và báo cáo: Viết báo cáo, làm slide thuyết trình, demo 1 tuần Trần Trọng Thuận - Bùi Ngọc Sơn hệ thống AI quiz agent hoàn chỉnh. Từ ngày 18/11 đến ngày 25/11 ​ ​ Đồng Nai, Ngày 09 tháng 10 năm 2025 GVHD​ Sinh viên đại diện​ ​ (Ký tên và ghi rõ họ tên)​ (Ký tên và ghi rõ họ tên) ​ Nguyễn Minh Sơn​ Bùi Ngọc Sơn', NULL),
(28, 4, 'PTUD_M4_Biểu mẫu thuyết minh đề tài.pdf', 'PDF', '2025-10-29 00:08:29', NULL, 'Đăng ký thuyết minh đề tài Học phần phát triển ứng dụng — O0O — 1.​ Thông tin sinh viên MSSV (Đại diện): 122001281 Họ và tên (Đại diện): Bùi Ngọc Sơn Danh sách sinh viên trong nhóm: STT MSSV Họ và tên Ký tên 01 122000860 Trần Trọng Thuận 02 122001281 Bùi Ngọc Sơn 2.​ Thông tin giáo viên hướng dẫn Họ và tên GV: Nguyễn Minh Sơn Điện thoại: 0946 734 111 Email: nmson@lhu.edu.vn 3.​ Tên dự án/ đề tài (dự kiến) thực hiện trong học phần Ứng dụng Web tự động tạo câu hỏi trắc nghiệm từ tài liệu (giáo trình, ghi âm, bài báo) 4.​ Tóm tắt đề tài Đề tài “Hệ thống sinh câu hỏi trắc nghiệm” nhằm xây dựng một công cụ tự động có khả năng tóm tắt nội dung từ tài liệu, bài giảng hoặc ghi âm, sau đó sinh ra các câu hỏi trắc nghiệm gồm câu hỏi, đáp án đúng và các đáp án nhiễu. Hệ thống được ứng dụng trong giáo dục và doanh nghiệp, giúp giảng viên, quản lý hoặc người đào tạo nhanh chóng kiểm tra mức độ hiểu của người học hoặc nhân viên, đồng thời tiết kiệm thời gian soạn đề, nâng cao hiệu quả đánh giá và đào tạo. 5.​ Mục tiêu và kết quả mong đợi Mục tiêu của đề tài: ●​ Xây dựng AI agent có khả năng đọc – hiểu nội dung từ file PDF, DOCX hoặc file âm thanh. ●​ Sinh câu hỏi trắc nghiệm gồm câu hỏi, đáp án đúng và đáp án nhiễu. ●​ Ứng dụng được cho nhiều lĩnh vực: giáo dục, doanh nghiệp, đào tạo nội bộ, và nghiên cứu. ●​ Ứng dụng xử lý ngôn ngữ tự nhiên (NLP) và Machine Learning để đảm bảo chất lượng câu hỏi. Tóm tắt và trích xuất ý chính của tài liệu một cách tự nhiên. Kết quả của đề tài: ●​ Hệ thống AI có khả năng xử lý nhanh, chính xác và sinh câu hỏi chất lượng cao. ●​ Web app thân thiện cho phép người dùng upload tài liệu hoặc ghi âm để sinh câu hỏi tự động. ●​ Lưu trữ và quản lý ngân hàng câu hỏi để tái sử dụng trong giảng dạy và đào tạo. ●​ Nâng cao hiệu quả học tập và đào tạo, giúp đánh giá nhanh, khách quan và chính xác. Hệ thống cho phép người dùng, ●​ Giảng viên: tạo đề nhanh, tiết kiệm thời gian, đánh giá mức độ tiếp thu của học sinh. ●​ Học sinh, sinh viên: ôn tập, luyện tập và tự kiểm tra kiến thức. ●​ Doanh nghiệp: kiểm tra mức độ hiểu của nhân viên sau các buổi họp hoặc đào tạo. ●​ Quản lý đào tạo: theo dõi, tổng hợp kết quả và cải thiện nội dung giảng dạy. 6.​ Kế hoạch thực hiện STT Nội dung thực hiện Thời gian Người thực hiện 01 Khảo sát & phân tích yêu cầu: Tìm hiểu các hệ thống AI tương tự (Gemini, ChatGPT, AutoQuiz AI); xác định yêu cầu đầu vào (file PDF, DOCX, audio) và đầu ra (summary + MCQ JSON). 1 tuần Từ ngày 30/09 đến ngày 7/10 Trần Trọng Thuận - Bùi Ngọc Sơn 02 Thiết kế kiến trúc tổng thể: Luồng xử lý giữa Web – Backend – Gemini API – DataBase; thiết kế ERD, DFD và luồng dữ liệu. 1 tuần Từ ngày 7/10 đến ngày 14/10 Trần Trọng Thuận - Bùi Ngọc Sơn 03 Xây dựng AI Agent tóm tắt nội dung: Tích hợp Gemini API để tóm tắt văn bản hoặc file âm thanh. Chuẩn hóa dữ liệu đầu vào. 1 tuần Từ ngày 14/10 đến ngày 21/10 Trần Trọng Thuận - Bùi Ngọc Sơn 04 Xây dựng AI Agent sinh câu hỏi: Sử dụng tóm tắt từ bước trước để sinh câu hỏi trắc nghiệm. Đảm bảo có 1 đáp đúng và 3 đáp nhiễu; định dạng JSON chuẩn. 1 tuần Từ ngày 21/10 đến ngày 28/10 Trần Trọng Thuận - Bùi Ngọc Sơn 05 Xây dựng hệ thống quản lý câu hỏi: Thêm, sửa, xóa, phân loại, export câu hỏi; hỗ trợ đa người dùng. 1 tuần Từ ngày 28/10 đến ngày 4/11 Trần Trọng Thuận - Bùi Ngọc Sơn 06 Phát triển giao diện web & API: Xây dựng giao diện upload tài liệu, hiển thị tóm tắt và câu hỏi; kết nối FastAPI backend với DeepSeek; hoàn thiện trải nghiệm người dùng. 1 tuần Từ ngày 4/11 đến ngày 11/11 Trần Trọng Thuận - Bùi Ngọc Sơn 07 Kiểm thử, tối ưu & bảo mật: Đánh giá chất lượng câu hỏi, tốc độ phản hồi API, xử lý tệp lớn, giới hạn request, ẩn API key, bảo mật dữ liệu người dùng. 1 tuần Từ ngày 11/11 đến ngày 18/11 Trần Trọng Thuận - Bùi Ngọc Sơn 08 Hoàn thiện và báo cáo: Viết báo cáo, làm slide thuyết trình, demo 1 tuần Trần Trọng Thuận - Bùi Ngọc Sơn hệ thống AI quiz agent hoàn chỉnh. Từ ngày 18/11 đến ngày 25/11 ​ ​ Đồng Nai, Ngày 09 tháng 10 năm 2025 GVHD​ Sinh viên đại diện​ ​ (Ký tên và ghi rõ họ tên)​ (Ký tên và ghi rõ họ tên) ​ Nguyễn Minh Sơn​ Bùi Ngọc Sơn', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `QuestionEvaluations`
--

CREATE TABLE `QuestionEvaluations` (
  `evaluation_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `model_version` varchar(100) NOT NULL,
  `evaluated_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL,
  `total_score` int(11) NOT NULL,
  `accuracy_score` int(11) DEFAULT 0,
  `alignment_score` int(11) DEFAULT 0,
  `distractors_score` int(11) DEFAULT 0,
  `clarity_score` int(11) DEFAULT 0,
  `status_by_agent` varchar(20) DEFAULT 'need_review',
  `raw_response_json` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

--
-- Dumping data for table `QuestionEvaluations`
--

INSERT INTO `QuestionEvaluations` (`evaluation_id`, `question_id`, `model_version`, `evaluated_at`, `updated_at`, `total_score`, `accuracy_score`, `alignment_score`, `distractors_score`, `clarity_score`, `status_by_agent`, `raw_response_json`) VALUES
(5, 62, 'gemini-2.5-flash', '2025-10-28 09:55:55', NULL, 86, 45, 20, 17, 4, 'accepted', '{\"context\": \"Hệ thống cho phép người dùng, ● Giảng viên: tạo đề nhanh, tiết kiệm thời gian, đánh giá mức độ tiếp thu của học sinh. ● Học sinh, sinh viên: ôn tập, luyện tập và tự kiểm tra kiến thức.\", \"question\": \"Lợi ích chính mà hệ thống mang lại cho Giảng viên là gì theo phần \\\"Kết quả của đề tài\\\"?\", \"options\": [\"A. Tự ôn tập và luyện tập kiến thức.\", \"B. Tạo đề nhanh, tiết kiệm thời gian và đánh giá mức độ tiếp thu của học sinh.\", \"C. Theo dõi, tổng hợp kết quả và cải thiện nội dung giảng dạy.\", \"D. Kiểm tra mức độ hiểu của nhân viên sau các buổi họp.\", \"E. \"], \"answer_letter\": \"B\", \"score\": 86, \"status\": \"accepted\", \"_eval_breakdown\": {\"accuracy\": 45, \"alignment\": 20, \"distractors\": 17, \"clarity\": 4}}'),
(6, 63, 'gemini-2.5-flash', '2025-10-29 00:08:29', NULL, 100, 50, 25, 20, 5, 'accepted', '{\"context\": \"3. Tên dự án/ đề tài (dự kiến) thực hiện trong học phần Ứng dụng Web tự động tạo câu hỏi trắc nghiệm từ tài liệu (giáo trình, ghi âm, bài báo)\", \"question\": \"Tên đầy đủ của dự án/đề tài được đề xuất thực hiện trong học phần này là gì?\", \"options\": [\"A. Hệ thống sinh câu hỏi trắc nghiệm tự động\", \"B. Ứng dụng Web tự động tạo câu hỏi trắc nghiệm từ tài liệu\", \"C. Công cụ tóm tắt và tạo câu hỏi trắc nghiệm\", \"D. AI Agent hỗ trợ giáo dục và đào tạo\"], \"answer_letter\": \"B\", \"score\": 100, \"status\": \"accepted\", \"_eval_breakdown\": {\"accuracy\": 50, \"alignment\": 25, \"distractors\": 20, \"clarity\": 5}}'),
(7, 64, 'gemini-2.5-flash', '2025-10-29 00:08:29', NULL, 98, 50, 25, 18, 5, 'accepted', '{\"context\": \"Đề tài “Hệ thống sinh câu hỏi trắc nghiệm” nhằm xây dựng một công cụ tự động có khả năng tóm tắt nội dung từ tài liệu, bài giảng hoặc ghi âm, sau đó sinh ra các câu hỏi trắc nghiệm gồm câu hỏi, đáp án đúng và các đáp án nhiễu. Hệ thống được ứng dụng trong giáo dục và doanh nghiệp, giúp giảng viên, quản lý hoặc người đào tạo nhanh chóng kiểm tra mức độ hiểu của người học hoặc nhân viên, đồng thời tiết kiệm thời gian soạn đề, nâng cao hiệu quả đánh giá và đào tạo.\", \"question\": \"Mục đích chính của đề tài “Hệ thống sinh câu hỏi trắc nghiệm” là gì?\", \"options\": [\"A. Xây dựng nền tảng học trực tuyến cho sinh viên.\", \"B. Phát triển công cụ tự động tóm tắt nội dung và sinh câu hỏi trắc nghiệm.\", \"C. Tạo ra một hệ thống quản lý ngân hàng câu hỏi đa năng.\", \"D. Tối ưu hóa quy trình kiểm tra đánh giá của doanh nghiệp.\"], \"answer_letter\": \"B\", \"score\": 98, \"status\": \"accepted\", \"_eval_breakdown\": {\"accuracy\": 50, \"alignment\": 25, \"distractors\": 18, \"clarity\": 5}}'),
(8, 65, 'gemini-2.5-flash', '2025-10-29 00:08:29', NULL, 100, 50, 25, 20, 5, 'accepted', '{\"context\": \"Mục tiêu của đề tài: ●​ Xây dựng AI agent có khả năng đọc – hiểu nội dung từ file PDF, DOCX hoặc file âm thanh. ●​ Sinh câu hỏi trắc nghiệm gồm câu hỏi, đáp án đúng và đáp án nhiễu.\", \"question\": \"Theo mục tiêu của đề tài, AI agent sẽ có khả năng đọc – hiểu nội dung từ những định dạng file nào?\", \"options\": [\"A. TXT, JPG, MP3\", \"B. PDF, DOCX hoặc file âm thanh\", \"C. PPTX, XLSX, video\", \"D. CSV, HTML, file hình ảnh\"], \"answer_letter\": \"B\", \"score\": 100, \"status\": \"accepted\", \"_eval_breakdown\": {\"accuracy\": 50, \"alignment\": 25, \"distractors\": 20, \"clarity\": 5}}');

-- --------------------------------------------------------

--
-- Table structure for table `Questions`
--

CREATE TABLE `Questions` (
  `question_id` int(11) NOT NULL,
  `source_file_id` int(11) DEFAULT NULL,
  `creator_id` int(11) DEFAULT NULL,
  `latest_evaluation_id` int(11) DEFAULT NULL,
  `question_text` longtext NOT NULL,
  `options` longtext NOT NULL,
  `answer_letter` char(1) NOT NULL,
  `status` varchar(20) DEFAULT 'TEMP',
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

--
-- Dumping data for table `Questions`
--

INSERT INTO `Questions` (`question_id`, `source_file_id`, `creator_id`, `latest_evaluation_id`, `question_text`, `options`, `answer_letter`, `status`, `created_at`, `updated_at`) VALUES
(6, 9, 3, NULL, 'Ch?c n?ng c?t lõi c?a ?? tài \"H? th?ng sinh câu h?i tr?c nghi?m\" là gì?', '[\"A. Xây dựng công cụ ghi âm bài giảng và chuyển đổi thành văn bản.\", \"B. Tóm tắt nội dung từ tài liệu và tự động sinh câu hỏi trắc nghiệm.\", \"C. Chỉ phân tích dữ liệu và đưa ra gợi ý cho việc soạn đề thủ công.\", \"D. Quản lý hồ sơ học sinh và nhân viên trong giáo dục và doanh nghiệp.\"]', 'B', 'accepted', '2025-10-24 14:35:51', NULL),
(7, 10, 3, NULL, 'M?c ?ích chính c?a ?? tài \"H? th?ng sinh câu h?i tr?c nghi?m\" là gì?', '[\"A. Phát triển một ứng dụng web để quản lý ngân hàng câu hỏi.\", \"B. Tạo ra một hệ thống chỉ dùng cho mục đích giáo dục.\", \"C. Xây dựng công cụ tự động tóm tắt nội dung và sinh câu hỏi trắc nghiệm từ tài liệu.\", \"D. Nghiên cứu sâu về các thuật toán Machine Learning.\"]', 'C', 'accepted', '2025-10-24 14:38:52', NULL),
(8, 10, 3, NULL, 'Theo m?c tiêu ?? ra, AI agent trong ?? tài này c?n có kh? n?ng chính nào?', '[\"A. Chỉ tóm tắt nội dung từ file PDF và DOCX.\", \"B. Đọc – hiểu nội dung từ các loại file và sinh câu hỏi trắc nghiệm.\", \"C. Phân tích dữ liệu người dùng để cải thiện thuật toán.\", \"D. Quản lý ngân hàng câu hỏi và thống kê kết quả học tập.\"]', 'B', 'accepted', '2025-10-24 14:38:52', NULL),
(9, 10, 3, NULL, '?? ??m b?o ch?t l??ng câu h?i và kh? n?ng tóm t?t t? nhiên, ?? tài d? ki?n s? ?ng d?ng nh?ng công ngh? nào?', '[\"A. Công nghệ nhận dạng giọng nói và tổng hợp giọng nói.\", \"B. Xây dựng giao diện web và API.\", \"C. Xử lý ngôn ngữ tự nhiên (NLP) và Machine Learning.\", \"D. Cơ sở dữ liệu quan hệ và điện toán đám mây.\"]', 'C', 'accepted', '2025-10-24 14:38:52', NULL),
(10, 10, 3, NULL, '??i t??ng ng??i dùng nào KHÔNG ???c li?t kê c? th? là ng??i h??ng l?i tr?c ti?p t? h? th?ng trong ph?n \"K?t qu? c?a ?? tài\"?', '[\"A. Giảng viên.\", \"B. Học sinh, sinh viên.\", \"C. Các nhà nghiên cứu AI.\", \"D. Quản lý đào tạo.\"]', 'C', 'accepted', '2025-10-24 14:38:52', NULL),
(11, 10, 3, NULL, 'Theo k? ho?ch th?c hi?n, b??c ??u tiên c?a ?? tài là gì và kéo dài trong bao lâu?', '[\"A. Thiết kế kiến trúc tổng thể, kéo dài 1 tuần.\", \"B. Khảo sát & phân tích yêu cầu, kéo dài 1 tuần.\", \"C. Xây dựng AI Agent tóm tắt nội dung, kéo dài 1 tuần.\", \"D. Hoàn thiện và báo cáo, kéo dài 1 tuần.\"]', 'B', 'accepted', '2025-10-24 14:38:52', NULL),
(12, 11, 3, NULL, 'Tên g?i chính th?c c?a d? án ???c ?? xu?t trong h?c ph?n là gì?', '[\"A. H? th?ng qu?n lý ngân hàng câu h?i\", \"B. ?ng d?ng Web t? ??ng t?o câu h?i tr?c nghi?m t? tài li?u (giáo trình, ghi âm, bài báo)\", \"C. Công c? tóm t?t n?i dung tài li?u\", \"D. H? th?ng ?ánh giá hi?u qu? ?ào t?o\"]', 'B', 'accepted', '2025-10-24 14:51:15', NULL),
(13, 11, 3, NULL, '?? ??m b?o ch?t l??ng c?a câu h?i sinh ra, ?? tài d? ki?n s? ?ng d?ng nh?ng công ngh? nào?', '[\"A. Big Data và Cloud Computing\", \"B. X? lý ngôn ng? t? nhiên (NLP) và Machine Learning\", \"C. H? th?ng qu?n lý c? s? d? li?u (DBMS) và Web Framework\", \"D. Công ngh? m?ng và b?o m?t thông tin\"]', 'B', 'accepted', '2025-10-24 14:51:15', NULL),
(14, 11, 3, NULL, 'Theo k?t qu? mong ??i c?a ?? tài, gi?ng viên s? nh?n ???c l?i ích c? th? nào khi s? d?ng h? th?ng?', '[\"A. Qu?n lý toàn b? quá trình ?ào t?o và h?c t?p.\", \"B. Theo dõi và t?ng h?p k?t qu? c?a h?c sinh.\", \"C. T?o ?? nhanh, ti?t ki?m th?i gian, ?ánh giá m?c ?? ti?p thu c?a h?c sinh.\", \"D. T?i lên tài li?u và ghi âm ?? sinh câu h?i t? ??ng.\"]', 'C', 'accepted', '2025-10-24 14:51:15', NULL),
(15, 11, 3, NULL, 'AI agent ???c xây d?ng trong ?? tài có kh? n?ng ??c và hi?u n?i dung t? nh?ng ??nh d?ng file nào?', '[\"A. Ch? file v?n b?n nh? TXT và RTF.\", \"B. File PDF, DOCX ho?c file âm thanh.\", \"C. File hình ?nh và video.\", \"D. File b?ng tính nh? XLS và CSV.\"]', 'B', 'accepted', '2025-10-24 14:51:15', NULL),
(16, 11, 3, NULL, 'Trong k? ho?ch th?c hi?n, n?i dung chính c?a b??c th? 4 là gì?', '[\"A. Kh?o sát và phân tích yêu c?u c?a h? th?ng.\", \"B. Thi?t k? ki?n trúc t?ng th? c?a h? th?ng.\", \"C. Xây d?ng AI Agent sinh câu h?i.\", \"D. Phát tri?n giao di?n web và API.\"]', 'C', 'accepted', '2025-10-24 14:51:15', NULL),
(44, 23, 2, NULL, 'Trong th? t?c `sp_SaveQuestion`, lo?i d? li?u nào ???c s? d?ng cho tham s? `p_options_json`?', '[\"A. TEXT\", \"B. VARCHAR(50)\", \"C. JSON\", \"D. CHAR(1)\"]', 'C', 'accepted', '2025-10-24 16:05:11', NULL),
(45, 23, 2, NULL, 'Sau khi chèn d? li?u vào b?ng `Files`, th? t?c `sp_SaveFile` th?c hi?n thao tác nào khác?', '[\"A. Cập nhật trường `file_type` của bản ghi vừa chèn.\", \"B. Trả về ID của bản ghi vừa được chèn.\", \"C. Xóa các bản ghi `Files` cũ hơn một tháng.\", \"D. Chèn một bản ghi mới vào bảng `Questions`.\"]', 'B', 'accepted', '2025-10-24 16:05:11', NULL),
(46, 23, 2, NULL, 'Trong th? t?c `sp_SaveFile`, lo?i d? li?u nào ???c s? d?ng cho tham s? `p_raw_text`?', '[\"A. VARCHAR(255)\", \"B. TEXT\", \"C. LONGTEXT\", \"D. JSON\"]', 'C', 'accepted', '2025-10-24 16:05:11', NULL),
(47, 24, 2, NULL, 'Th? t?c l?u tr? `sp_SaveQuestion` ???c thi?t k? ?? chèn d? li?u vào b?ng nào trong c? s? d? li?u?', '[\"A. Files\", \"B. Questions\", \"C. Procedures\", \"D. sp_SaveQuestion\"]', 'B', 'accepted', '2025-10-24 16:09:41', NULL),
(48, 24, 2, NULL, 'Sau khi chèn d? li?u vào b?ng, th? t?c `sp_SaveFile` tr? v? thông tin gì thông qua câu l?nh `SELECT`?', '[\"A. p_uploader_id\", \"B. filename\", \"C. file_id\", \"D. uploaded_at\"]', 'C', 'accepted', '2025-10-24 16:09:41', NULL),
(49, 24, 2, NULL, 'Trong th? t?c `sp_SaveQuestion`, tr??ng d? li?u nào trong b?ng `Questions` ???c t? ??ng gán giá tr? th?i gian hi?n t?i (`NOW()`) mà không c?n truy?n qua tham s? ??u vào?', '[\"A. status\", \"B. question_text\", \"C. created_at\", \"D. options\"]', 'C', 'accepted', '2025-10-24 16:09:41', NULL),
(50, 25, 2, NULL, 'Mục tiêu chính của ứng dụng Web được đề xuất là gì?', '[\"A. Chuyển đổi định dạng tài liệu giữa PDF, DOCX và ghi âm.\", \"B. Tự động tạo câu hỏi trắc nghiệm hoàn chỉnh từ nhiều loại tài liệu bằng AI.\", \"C. Phát triển các API AI mới chuyên về tóm tắt văn bản và sinh câu hỏi.\", \"D. Quản lý các tài liệu PDF, DOCX và ghi âm cho người dùng cuối.\"]', 'B', 'accepted', '2025-10-24 16:40:50', NULL),
(51, 25, 2, NULL, 'Các công nghệ chính được ứng dụng trong hệ thống tạo câu hỏi trắc nghiệm này bao gồm những gì?', '[\"A. Blockchain, Internet of Things và điện toán đám mây.\", \"B. Xử lý ngôn ngữ tự nhiên (NLP), Machine Learning và API AI.\", \"C. Phân tích dữ liệu lớn, thị giác máy tính và thực tế ảo.\", \"D. Lập trình di động, phát triển game và hệ thống nhúng.\"]', 'B', 'accepted', '2025-10-24 16:40:50', NULL),
(52, 25, 2, NULL, 'Ai là các thành viên của nhóm thực hiện và người hướng dẫn dự án?', '[\"A. Bùi Minh Sơn, Trần Trọng Thuận và Nguyễn Ngọc Sơn.\", \"B. Bùi Ngọc Sơn, Trần Trọng Thuận và GV Nguyễn Minh Sơn.\", \"C. Trần Trọng Sơn, Bùi Ngọc Thuận và GV Nguyễn Minh Sơn.\", \"D. Nguyễn Minh Sơn và Bùi Ngọc Sơn.\"]', 'B', 'accepted', '2025-10-24 16:40:50', NULL),
(53, 26, 3, NULL, 'Mục đích chính của đề tài “Hệ thống sinh câu hỏi trắc nghiệm” là gì?', '[\"A. Xây dựng một công cụ chỉ để tóm tắt nội dung từ tài liệu.\", \"B. Phát triển một công cụ tự động tóm tắt nội dung và sinh câu hỏi trắc nghiệm.\", \"C. Tạo ra một hệ thống chỉ để quản lý ngân hàng câu hỏi.\", \"D. Giúp sinh viên làm bài tập trắc nghiệm trực tuyến mà không cần giáo viên.\"]', 'B', 'accepted', '2025-10-24 18:21:59', NULL),
(54, 26, 3, NULL, 'Theo mục tiêu của đề tài, AI agent được xây dựng có khả năng xử lý những loại định dạng tài liệu nào?', '[\"A. Chỉ file PDF và DOCX.\", \"B. File PDF, DOCX và file âm thanh.\", \"C. File hình ảnh và video.\", \"D. Chỉ file âm thanh.\"]', 'B', 'accepted', '2025-10-24 18:21:59', NULL),
(55, 26, 3, NULL, 'Đối với giảng viên, hệ thống “Hệ thống sinh câu hỏi trắc nghiệm” mang lại lợi ích gì?', '[\"A. Theo dõi và tổng hợp kết quả của học sinh.\", \"B. Tự ôn tập và luyện tập kiến thức.\", \"C. Tạo đề nhanh, tiết kiệm thời gian và đánh giá mức độ tiếp thu của học sinh.\", \"D. Kiểm tra mức độ hiểu của nhân viên sau các buổi đào tạo.\"]', 'C', 'accepted', '2025-10-24 18:21:59', NULL),
(56, 26, 3, NULL, 'Để đảm bảo chất lượng câu hỏi và tóm tắt tài liệu một cách tự nhiên, đề tài dự kiến sẽ ứng dụng những công nghệ nào?', '[\"A. Xử lý đồ họa và thiết kế web.\", \"B. Xử lý ngôn ngữ tự nhiên (NLP) và Machine Learning.\", \"C. Phân tích dữ liệu lớn và điện toán đám mây.\", \"D. Hệ thống quản lý cơ sở dữ liệu và mạng máy tính.\"]', 'B', 'accepted', '2025-10-24 18:22:00', NULL),
(61, 27, 3, NULL, '\"Để đảm bảo chất lượng câu hỏi được sinh ra, đề tài dự kiến sẽ ứng dụng những công nghệ nào?\"', '[\"A. Công nghệ tóm tắt văn bản và công nghệ ghi âm.\", \"B. Xử lý ngôn ngữ tự nhiên (NLP) và Machine Learning.\", \"C. Phát triển giao diện web và API.\", \"D. Quản lý cơ sở dữ liệu và hệ thống lưu trữ.\", \"E. \"]', 'B', 'accepted', '2025-10-28 09:55:55', NULL),
(62, 27, 3, 5, '\"Lợi ích chính mà hệ thống mang lại cho Giảng viên là gì theo phần \\\"Kết quả của đề tài\\\"?\"', '[\"A. Tự ôn tập và luyện tập kiến thức.\", \"B. Tạo đề nhanh, tiết kiệm thời gian và đánh giá mức độ tiếp thu của học sinh.\", \"C. Theo dõi, tổng hợp kết quả và cải thiện nội dung giảng dạy.\", \"D. Kiểm tra mức độ hiểu của nhân viên sau các buổi họp.\", \"E. \"]', 'B', 'accepted', '2025-10-28 09:55:55', NULL),
(63, 28, 4, 6, '\"Tên đầy đủ của dự án/đề tài được đề xuất thực hiện trong học phần này là gì?\"', '[\"A. Hệ thống sinh câu hỏi trắc nghiệm tự động\", \"B. Ứng dụng Web tự động tạo câu hỏi trắc nghiệm từ tài liệu\", \"C. Công cụ tóm tắt và tạo câu hỏi trắc nghiệm\", \"D. AI Agent hỗ trợ giáo dục và đào tạo\"]', 'B', 'accepted', '2025-10-29 00:08:29', NULL),
(64, 28, 4, 7, '\"Mục đích chính của đề tài “Hệ thống sinh câu hỏi trắc nghiệm” là gì?\"', '[\"A. Xây dựng nền tảng học trực tuyến cho sinh viên.\", \"B. Phát triển công cụ tự động tóm tắt nội dung và sinh câu hỏi trắc nghiệm.\", \"C. Tạo ra một hệ thống quản lý ngân hàng câu hỏi đa năng.\", \"D. Tối ưu hóa quy trình kiểm tra đánh giá của doanh nghiệp.\"]', 'B', 'accepted', '2025-10-29 00:08:29', NULL),
(65, 28, 4, 8, '\"Theo mục tiêu của đề tài, AI agent sẽ có khả năng đọc – hiểu nội dung từ những định dạng file nào?\"', '[\"A. TXT, JPG, MP3\", \"B. PDF, DOCX hoặc file âm thanh\", \"C. PPTX, XLSX, video\", \"D. CSV, HTML, file hình ảnh\"]', 'B', 'accepted', '2025-10-29 00:08:29', NULL),
(66, 28, 4, NULL, '\"Hệ thống sinh câu hỏi trắc nghiệm này dự kiến sẽ được ứng dụng trong những lĩnh vực chính nào?\"', '[\"A. Chỉ trong lĩnh vực nghiên cứu khoa học.\", \"B. Giáo dục và doanh nghiệp.\", \"C. Chủ yếu trong các cơ quan chính phủ.\", \"D. Dành riêng cho học sinh, sinh viên tự ôn tập.\"]', 'B', 'accepted', '2025-10-29 00:08:29', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `SessionResults`
--

CREATE TABLE `SessionResults` (
  `result_id` int(11) NOT NULL,
  `session_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `selected_option` char(1) DEFAULT NULL,
  `is_correct` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

--
-- Dumping data for table `SessionResults`
--

INSERT INTO `SessionResults` (`result_id`, `session_id`, `question_id`, `selected_option`, `is_correct`) VALUES
(1, 1, 55, 'A', 0),
(2, 1, 56, 'A', 0),
(3, 1, 61, 'A', 0),
(5, 2, 64, 'A', 0),
(6, 2, 65, 'A', 0),
(7, 2, 66, 'B', 1),
(8, 3, 64, 'A', 0),
(9, 3, 65, 'A', 0),
(10, 3, 66, 'A', 0),
(12, 5, 64, 'A', 0),
(13, 5, 65, 'A', 0),
(14, 5, 66, 'A', 0);

-- --------------------------------------------------------

--
-- Table structure for table `Users`
--

CREATE TABLE `Users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `is_active` tinyint(1) DEFAULT 1,
  `is_admin` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vietnamese_ci;

--
-- Dumping data for table `Users`
--

INSERT INTO `Users` (`user_id`, `username`, `email`, `password_hash`, `created_at`, `is_active`, `is_admin`) VALUES
(1, 'string', 'user@example.com', '$2b$12$j/j3hnbIMK4A1wSncSQvgejE6bjksWLrRGTt3AVIFU2zYCxQcICeK', '2025-10-22 21:14:48', 1, 0),
(2, 'testabc', 'testabc@gmail.com', '$2b$12$HiQBUKSZbbjh1XsMGA3zxOcd36XB9EpOuHUg7yyaDL99HyLRtt53m', '2025-10-24 10:06:44', 1, 1),
(3, 'thuan', 'thuan@gmail.com', '$2b$12$Kzw/ORY0pSHSwFfc5dz9jOwhGDZ41AwyPcOY.966nPiTcA1RBGoU2', '2025-10-24 13:21:55', 1, 1),
(4, 'nhat', 'nhat@gmail.com', '$2b$12$jcCuM.kx3y0hP0.lLNH9EuYnTgCLCV/pso/9NQIRKgjePybaEosYO', '2025-10-29 00:07:05', 1, 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ExamQuestions`
--
ALTER TABLE `ExamQuestions`
  ADD PRIMARY KEY (`exam_question_id`),
  ADD UNIQUE KEY `exam_id` (`exam_id`,`question_id`),
  ADD KEY `question_id` (`question_id`);

--
-- Indexes for table `Exams`
--
ALTER TABLE `Exams`
  ADD PRIMARY KEY (`exam_id`),
  ADD UNIQUE KEY `share_token` (`share_token`),
  ADD KEY `owner_id` (`owner_id`);

--
-- Indexes for table `ExamSessions`
--
ALTER TABLE `ExamSessions`
  ADD PRIMARY KEY (`session_id`),
  ADD KEY `exam_id` (`exam_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `Files`
--
ALTER TABLE `Files`
  ADD PRIMARY KEY (`file_id`),
  ADD KEY `uploader_id` (`uploader_id`);

--
-- Indexes for table `QuestionEvaluations`
--
ALTER TABLE `QuestionEvaluations`
  ADD PRIMARY KEY (`evaluation_id`),
  ADD KEY `question_id` (`question_id`);

--
-- Indexes for table `Questions`
--
ALTER TABLE `Questions`
  ADD PRIMARY KEY (`question_id`),
  ADD KEY `source_file_id` (`source_file_id`),
  ADD KEY `creator_id` (`creator_id`),
  ADD KEY `FK_LatestEvaluation` (`latest_evaluation_id`);

--
-- Indexes for table `SessionResults`
--
ALTER TABLE `SessionResults`
  ADD PRIMARY KEY (`result_id`),
  ADD UNIQUE KEY `session_id` (`session_id`,`question_id`),
  ADD KEY `question_id` (`question_id`);

--
-- Indexes for table `Users`
--
ALTER TABLE `Users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `ExamQuestions`
--
ALTER TABLE `ExamQuestions`
  MODIFY `exam_question_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `Exams`
--
ALTER TABLE `Exams`
  MODIFY `exam_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `ExamSessions`
--
ALTER TABLE `ExamSessions`
  MODIFY `session_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `Files`
--
ALTER TABLE `Files`
  MODIFY `file_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `QuestionEvaluations`
--
ALTER TABLE `QuestionEvaluations`
  MODIFY `evaluation_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `Questions`
--
ALTER TABLE `Questions`
  MODIFY `question_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=68;

--
-- AUTO_INCREMENT for table `SessionResults`
--
ALTER TABLE `SessionResults`
  MODIFY `result_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `Users`
--
ALTER TABLE `Users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `ExamQuestions`
--
ALTER TABLE `ExamQuestions`
  ADD CONSTRAINT `ExamQuestions_ibfk_1` FOREIGN KEY (`exam_id`) REFERENCES `Exams` (`exam_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `ExamQuestions_ibfk_2` FOREIGN KEY (`question_id`) REFERENCES `Questions` (`question_id`) ON DELETE CASCADE;

--
-- Constraints for table `Exams`
--
ALTER TABLE `Exams`
  ADD CONSTRAINT `Exams_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `Users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `ExamSessions`
--
ALTER TABLE `ExamSessions`
  ADD CONSTRAINT `ExamSessions_ibfk_1` FOREIGN KEY (`exam_id`) REFERENCES `Exams` (`exam_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `ExamSessions_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`) ON DELETE SET NULL;

--
-- Constraints for table `Files`
--
ALTER TABLE `Files`
  ADD CONSTRAINT `Files_ibfk_1` FOREIGN KEY (`uploader_id`) REFERENCES `Users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `QuestionEvaluations`
--
ALTER TABLE `QuestionEvaluations`
  ADD CONSTRAINT `QuestionEvaluations_ibfk_1` FOREIGN KEY (`question_id`) REFERENCES `Questions` (`question_id`) ON DELETE CASCADE;

--
-- Constraints for table `Questions`
--
ALTER TABLE `Questions`
  ADD CONSTRAINT `FK_LatestEvaluation` FOREIGN KEY (`latest_evaluation_id`) REFERENCES `QuestionEvaluations` (`evaluation_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `Questions_ibfk_1` FOREIGN KEY (`source_file_id`) REFERENCES `Files` (`file_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `Questions_ibfk_2` FOREIGN KEY (`creator_id`) REFERENCES `Users` (`user_id`) ON DELETE SET NULL;

--
-- Constraints for table `SessionResults`
--
ALTER TABLE `SessionResults`
  ADD CONSTRAINT `SessionResults_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `ExamSessions` (`session_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `SessionResults_ibfk_2` FOREIGN KEY (`question_id`) REFERENCES `Questions` (`question_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
