-- COMP 440 Project Database
-- Updated for Phases 1, 2, and 3

DROP DATABASE IF EXISTS login_system;

CREATE DATABASE login_system;

USE login_system;

-- -----------------------------
-- User table
-- Phase 1 requirement:
-- user(username, password, firstName, lastName, email, phone)
-- -----------------------------

CREATE TABLE user (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    firstName VARCHAR(100) NOT NULL,
    lastName VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(50) NOT NULL UNIQUE
);

-- -----------------------------
-- Rental unit table
-- A rental is posted by exactly one registered user.
-- rental_id is auto generated.
-- created_at is used to enforce/check daily posting limits and Phase 3 date queries.
-- -----------------------------

CREATE TABLE rental_unit (
    rental_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    username VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rental_user FOREIGN KEY (username) REFERENCES user (username) ON DELETE CASCADE ON UPDATE CASCADE
);

-- -----------------------------
-- Rental feature table
-- Each rental can have many features.
-- Example:
-- rental_id = 1, feature = 'Wi-Fi'
-- rental_id = 1, feature = 'Kitchen'
-- rental_id = 1, feature = 'Mountainview'
-- -----------------------------

CREATE TABLE rental_feature (
    rental_id INT NOT NULL,
    feature VARCHAR(100) NOT NULL,
    PRIMARY KEY (rental_id, feature),
    CONSTRAINT fk_feature_rental FOREIGN KEY (rental_id) REFERENCES rental_unit (rental_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- -----------------------------
-- Review table
-- A user can review a rental at most once.
-- The app enforces:
-- 1. max 3 reviews per user per day
-- 2. no self-review
-- 3. no review modification
-- -----------------------------

CREATE TABLE review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    rental_id INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    score ENUM(
        'Excellent',
        'Good',
        'Fair',
        'Poor'
    ) NOT NULL,
    remark TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_rental_review (rental_id, username),
    CONSTRAINT fk_review_rental FOREIGN KEY (rental_id) REFERENCES rental_unit (rental_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_review_user FOREIGN KEY (username) REFERENCES user (username) ON DELETE CASCADE ON UPDATE CASCADE
);

-- -----------------------------
-- Helpful indexes for Phase 3 queries
-- -----------------------------

CREATE INDEX idx_rental_username_date ON rental_unit (username, created_at);

CREATE INDEX idx_rental_date ON rental_unit (created_at);

CREATE INDEX idx_feature_name ON rental_feature (feature);

CREATE INDEX idx_review_username_date ON review (username, created_at);

CREATE INDEX idx_review_rental_score ON review (rental_id, score);

CREATE INDEX idx_review_username_score ON review (username, score);