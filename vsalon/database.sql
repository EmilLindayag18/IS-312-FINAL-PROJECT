-- VSalon Database Schema for MySQL (XAMPP)
-- Import this via phpMyAdmin or mysql CLI

CREATE DATABASE IF NOT EXISTS vsalon_db;
USE vsalon_db;

-- Users table (customers + admins)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('customer', 'admin') DEFAULT 'customer',
    profile_image VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Staff table
CREATE TABLE staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    specialization VARCHAR(100),
    schedule TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Services table
CREATE TABLE services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    duration_minutes INT DEFAULT 30,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(50),
    image_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Appointments table
CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    service_id INT NOT NULL,
    staff_id INT,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status ENUM('pending', 'confirmed', 'completed', 'cancelled', 'rescheduled') DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(id),
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE SET NULL
);

-- Products table (Shop)
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    category VARCHAR(50),
    image_url VARCHAR(255),
    low_stock_threshold INT DEFAULT 5,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'cancelled') DEFAULT 'pending',
    payment_method ENUM('cash', 'card', 'online') DEFAULT 'cash',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Order Items table
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- POS Transactions
CREATE TABLE pos_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    appointment_id INT,
    amount DECIMAL(10,2) NOT NULL,
    payment_method ENUM('cash', 'card', 'online') DEFAULT 'cash',
    transaction_type ENUM('product_sale', 'service_payment') NOT NULL,
    processed_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL,
    FOREIGN KEY (processed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Inventory log
CREATE TABLE inventory_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    change_quantity INT NOT NULL,
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Insert default admin
INSERT INTO users (full_name, email, phone, password_hash, role)
VALUES ('Admin', 'admin@vsalon.com', '09000000000', 'pbkdf2:sha256:600000$salt$hash', 'admin');

-- Insert sample services
INSERT INTO services (name, description, duration_minutes, price, category) VALUES
('Haircut', 'Professional haircut and styling', 30, 300.00, 'Hair'),
('Hair Color', 'Full hair coloring service', 90, 1500.00, 'Hair'),
('Manicure', 'Classic manicure with polish', 45, 400.00, 'Nails'),
('Pedicure', 'Relaxing pedicure treatment', 60, 500.00, 'Nails'),
('Facial Treatment', 'Deep cleansing facial', 60, 800.00, 'Skin'),
('Hair Spa', 'Nourishing hair spa treatment', 60, 700.00, 'Hair'),
('Nail Art', 'Creative nail art designs', 60, 600.00, 'Nails'),
('Eyebrow Threading', 'Precise eyebrow shaping', 15, 150.00, 'Face');

-- Insert sample staff
INSERT INTO staff (full_name, email, phone, specialization) VALUES
('Maria Santos', 'maria@vsalon.com', '09111111111', 'Hair Styling'),
('Juan Dela Cruz', 'juan@vsalon.com', '09222222222', 'Hair Color Specialist'),
('Ana Reyes', 'ana@vsalon.com', '09333333333', 'Nail Technician'),
('Sofia Garcia', 'sofia@vsalon.com', '09444444444', 'Skin Care Specialist');

-- Insert sample products
INSERT INTO products (name, description, price, stock_quantity, category, low_stock_threshold) VALUES
('Shampoo Premium', 'Professional salon shampoo 500ml', 450.00, 25, 'Hair Care', 5),
('Conditioner Deluxe', 'Deep conditioning treatment 500ml', 500.00, 20, 'Hair Care', 5),
('Hair Serum', 'Anti-frizz hair serum 100ml', 350.00, 15, 'Hair Care', 3),
('Nail Polish Set', 'Set of 6 trendy nail polish colors', 600.00, 30, 'Nails', 5),
('Face Moisturizer', 'Hydrating face moisturizer 100ml', 550.00, 18, 'Skin Care', 4),
('Hair Wax', 'Strong hold styling wax 80g', 300.00, 22, 'Hair Care', 5);
