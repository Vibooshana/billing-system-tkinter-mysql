DROP DATABASE IF EXISTS billing_system;
CREATE DATABASE billing_system;
USE billing_system;

-- Product Table with optional category/theme
CREATE TABLE Product (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    price INT,
    stock INT,
    category VARCHAR(50)
);

-- Customer Table
CREATE TABLE Customer (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    phone VARCHAR(15)
);

-- Bill Table
CREATE TABLE Bill (
    bill_id INT PRIMARY KEY AUTO_INCREMENT,
    date DATE,
    total_amount INT,
    customer_name VARCHAR(50)
);

-- Bill Items Table
CREATE TABLE Bill_Items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    bill_id INT,
    product_id INT,
    quantity INT,
    subtotal INT,
    FOREIGN KEY (bill_id) REFERENCES Bill(bill_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

-- Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50)
);

-- Sample User
INSERT INTO users (username, password) VALUES ('root', '25@Viboo');

-- Sample Products (Theme: Grocery)
INSERT INTO Product (name, price, stock, category) VALUES
('Milk', 50, 100, 'Dairy'),
('Bread', 40, 50, 'Bakery'),
('Eggs', 6, 200, 'Dairy'),
('Chocolate', 20, 30, 'Snacks');


Select * from product;