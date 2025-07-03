SHOW DATABASES;
CREATE DATABASE taipei;
USE taipei;
SHOW TABLES;

DESC member;
DESC attraction;
DESC mrt;

SELECT * FROM member;
SELECT * FROM mrt;
SELECT * FROM attraction;
SELECT * FROM booking;
SELECT * FROM orders;
CREATE INDEX idx_attraction_name ON attraction(name);
CREATE INDEX idx_attraction_mrt ON attraction(mrt);
CREATE INDEX idx_mrt_mrt ON mrt(mrt);

CREATE TABLE member(	
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);
DROP TABLE booking;
CREATE TABLE booking(
    bookingId INT PRIMARY KEY AUTO_INCREMENT,
    userId INT UNSIGNED NOT NULL,
    attractionId INT UNSIGNED NOT NULL,
    date DATE NOT NULL,
    time VARCHAR(50) NOT NULL,
    price INT UNSIGNED NOT NULL
);

DROP TABLE orders;
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
	orderNumber VARCHAR(50) NOT NULL UNIQUE,
    bookingId INT UNSIGNED NOT NULL,
    attractionId INT UNSIGNED NOT NULL,
    userId INT UNSIGNED NOT NULL,
    date DATE NOT NULL,
    time VARCHAR(50) NOT NULL,
    price INT UNSIGNED NOT NULL,
    contactName VARCHAR(50) NOT NULL,
    contactEmail VARCHAR(50) NOT NULL,
    contactPhone VARCHAR(50) NOT NULL,
    status INT NOT NULL,
    orderTime DATETIME DEFAULT CURRENT_TIMESTAMP  -- 記錄下單時間
);