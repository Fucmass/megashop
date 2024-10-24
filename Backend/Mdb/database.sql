    CREATE DATABASE IF NOT EXISTS minishop;

    USE minishop;

    CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(320) NOT NULL UNIQUE,
        phone_number VARCHAR(20),  -- Optional
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    