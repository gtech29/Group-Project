-- Create the database if it doesn't already exist
CREATE DATABASE IF NOT EXISTS login_system;

-- Switch to the newly created database
USE login_system;

-- Create the user table
CREATE TABLE IF NOT EXISTS user (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    firstName VARCHAR(50) NOT NULL,
    lastName VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    );

-- Phase 2: Create the rental unit table
CREATE TABLE IF NOT EXISTS rental_unit (
    rental_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(50) NOT NULL,
    description VARCHAR(255) NOT NULL,
    feature VARCHAR(50) NOT NULL,
    price INT NOT NULL,
    username VARCHAR(50),
    FOREIGN KEY (username) REFERENCES user (username)
    );