-- ===========================================
-- Database: spdhlmjn_mcqs
-- Converted from Microsoft SQL Server
-- Compatible with MariaDB/MySQL
-- ===========================================

CREATE DATABASE IF NOT EXISTS `spdhlmjn_mcqs`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;
USE `spdhlmjn_mcqs`;

-- ===========================================
-- Table: Users
-- ===========================================
CREATE TABLE `Users` (
  `user_id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(255) NOT NULL UNIQUE,
  `email` VARCHAR(255) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `is_active` BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===========================================
-- Table: Files
-- ===========================================
CREATE TABLE `Files` (
  `file_id` INT AUTO_INCREMENT PRIMARY KEY,
  `uploader_id` INT NOT NULL,
  `filename` VARCHAR(500) NOT NULL,
  `file_type` VARCHAR(50) NOT NULL,
  `uploaded_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `storage_path` VARCHAR(500),
  `raw_text` LONGTEXT,
  `summary` LONGTEXT,
  FOREIGN KEY (`uploader_id`) REFERENCES `Users`(`user_id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===========================================
-- Table: Questions
-- ===========================================
CREATE TABLE `Questions` (
  `question_id` INT AUTO_INCREMENT PRIMARY KEY,
  `source_file_id` INT,
  `creator_id` INT,
  `latest_evaluation_id` INT,
  `question_text` LONGTEXT NOT NULL,
  `options` LONGTEXT NOT NULL,
  `answer_letter` CHAR(1) NOT NULL,
  `status` VARCHAR(20) DEFAULT 'TEMP',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`source_file_id`) REFERENCES `Files`(`file_id`) ON DELETE SET NULL,
  FOREIGN KEY (`creator_id`) REFERENCES `Users`(`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===========================================
-- Table: QuestionEvaluations
-- ===========================================
CREATE TABLE `QuestionEvaluations` (
  `evaluation_id` INT AUTO_INCREMENT PRIMARY KEY,
  `question_id` INT NOT NULL,
  `model_version` VARCHAR(100) NOT NULL,
  `evaluated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `total_score` INT NOT NULL,
  `accuracy_score` INT DEFAULT 0,
  `alignment_score` INT DEFAULT 0,
  `distractors_score` INT DEFAULT 0,
  `clarity_score` INT DEFAULT 0,
  `status_by_agent` VARCHAR(20) DEFAULT 'need_review',
  `raw_response_json` LONGTEXT,
  FOREIGN KEY (`question_id`) REFERENCES `Questions`(`question_id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Liên kết ngược tới latest_evaluation_id
ALTER TABLE `Questions`
  ADD CONSTRAINT `FK_LatestEvaluation`
  FOREIGN KEY (`latest_evaluation_id`)
  REFERENCES `QuestionEvaluations`(`evaluation_id`)
  ON DELETE SET NULL;

-- ===========================================
-- Table: Exams
-- ===========================================
CREATE TABLE `Exams` (
  `exam_id` INT AUTO_INCREMENT PRIMARY KEY,
  `owner_id` INT NOT NULL,
  `title` VARCHAR(500) NOT NULL,
  `description` LONGTEXT,
  `share_token` VARCHAR(50) NOT NULL UNIQUE,
  `is_public` BOOLEAN DEFAULT FALSE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`owner_id`) REFERENCES `Users`(`user_id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===========================================
-- Table: ExamQuestions
-- ===========================================
CREATE TABLE `ExamQuestions` (
  `exam_question_id` INT AUTO_INCREMENT PRIMARY KEY,
  `exam_id` INT NOT NULL,
  `question_id` INT NOT NULL,
  `order_index` INT NOT NULL,
  UNIQUE (`exam_id`, `question_id`),
  FOREIGN KEY (`exam_id`) REFERENCES `Exams`(`exam_id`)
    ON DELETE CASCADE,
  FOREIGN KEY (`question_id`) REFERENCES `Questions`(`question_id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===========================================
-- Table: ExamSessions (fixed for MariaDB)
-- ===========================================
CREATE TABLE `ExamSessions` (
  `session_id` INT AUTO_INCREMENT PRIMARY KEY,
  `exam_id` INT NOT NULL,
  `user_id` INT,
  `guest_name` VARCHAR(255),
  `start_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `end_time` DATETIME,
  `total_score` INT,
  FOREIGN KEY (`exam_id`) REFERENCES `Exams`(`exam_id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `Users`(`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===========================================
-- Table: SessionResults
-- ===========================================
CREATE TABLE `SessionResults` (
  `result_id` INT AUTO_INCREMENT PRIMARY KEY,
  `session_id` INT NOT NULL,
  `question_id` INT NOT NULL,
  `selected_option` CHAR(1),
  `is_correct` BOOLEAN,
  UNIQUE (`session_id`, `question_id`),
  FOREIGN KEY (`session_id`) REFERENCES `ExamSessions`(`session_id`) ON DELETE CASCADE,
  FOREIGN KEY (`question_id`) REFERENCES `Questions`(`question_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
