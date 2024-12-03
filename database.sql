CREATE DATABASE IF NOT EXISTS megashop;

USE megashop;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(320) NOT NULL UNIQUE,
    phone_number VARCHAR(20),  -- Optional
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    brand VARCHAR(45) NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    price VARCHAR (50) NOT NULL,
    stock VARCHAR (3) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO products('product_id', 'brand', 'product_name', 'price', 'stock')
