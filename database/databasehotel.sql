-- =====================================================
-- DATABASE: HỆ THỐNG QUẢN LÝ KHÁCH SẠN
-- PROJECT: TTCS_T926_K20C6_N5
-- =====================================================

CREATE DATABASE IF NOT EXISTS hotel_management
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE hotel_management;


-- =====================================================
-- 1. BẢNG TÀI KHOẢN
-- =====================================================

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'STAFF',
    status BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- 2. BẢNG KHÁCH HÀNG
-- =====================================================

CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    identity_number VARCHAR(30) UNIQUE,
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- 3. BẢNG LOẠI PHÒNG
-- =====================================================

CREATE TABLE room_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    price DECIMAL(12,2) NOT NULL,
    max_guests INT NOT NULL DEFAULT 1
);


-- =====================================================
-- 4. BẢNG PHÒNG
-- =====================================================

CREATE TABLE rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(20) NOT NULL UNIQUE,
    room_type_id INT NOT NULL,
    floor INT,
    status VARCHAR(30) NOT NULL DEFAULT 'AVAILABLE',
    description TEXT,

    CONSTRAINT fk_rooms_room_type
        FOREIGN KEY (room_type_id)
        REFERENCES room_types(id)
);


-- =====================================================
-- 5. BẢNG ĐẶT / THUÊ PHÒNG
-- =====================================================

CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    user_id INT NOT NULL,
    check_in_date DATETIME NOT NULL,
    check_out_date DATETIME NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'BOOKED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_bookings_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(id),

    CONSTRAINT fk_bookings_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
);


-- =====================================================
-- 6. CHI TIẾT ĐẶT PHÒNG
-- =====================================================

CREATE TABLE booking_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    room_id INT NOT NULL,
    price DECIMAL(12,2) NOT NULL,

    CONSTRAINT fk_booking_details_booking
        FOREIGN KEY (booking_id)
        REFERENCES bookings(id),

    CONSTRAINT fk_booking_details_room
        FOREIGN KEY (room_id)
        REFERENCES rooms(id)
);


-- =====================================================
-- 7. BẢNG HÓA ĐƠN
-- =====================================================

CREATE TABLE invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL UNIQUE,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    discount DECIMAL(12,2) NOT NULL DEFAULT 0,
    final_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    status VARCHAR(30) NOT NULL DEFAULT 'UNPAID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_invoices_booking
        FOREIGN KEY (booking_id)
        REFERENCES bookings(id)
);


-- =====================================================
-- 8. BẢNG THANH TOÁN
-- =====================================================

CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_id INT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(30) NOT NULL DEFAULT 'SUCCESS',

    CONSTRAINT fk_payments_invoice
        FOREIGN KEY (invoice_id)
        REFERENCES invoices(id)
);