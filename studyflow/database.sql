-- ══════════════════════════════════════════
--  StudyFlow Database Setup
--  Run this in MySQL before starting the app
-- ══════════════════════════════════════════

CREATE DATABASE IF NOT EXISTS studyflow;
USE studyflow;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    first_name   VARCHAR(50)  NOT NULL,
    last_name    VARCHAR(50)  NOT NULL DEFAULT '',
    email        VARCHAR(100) NOT NULL UNIQUE,
    password     VARCHAR(255) NOT NULL,
    student_type ENUM('school','university') DEFAULT 'university',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    name       VARCHAR(200) NOT NULL,
    category   ENUM('homework','assignment','exam','report','project') DEFAULT 'homework',
    priority   ENUM('high','medium','low') DEFAULT 'medium',
    subject    VARCHAR(100) DEFAULT '',
    deadline   DATE NOT NULL,
    notes      TEXT DEFAULT '',
    status     ENUM('pending','done') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Sample data (optional — remove if not needed)
-- INSERT INTO users (first_name,last_name,email,password,student_type)
-- VALUES ('Demo','Student','demo@studyflow.com', '<hashed_password>', 'university');
