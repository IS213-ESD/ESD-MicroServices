CREATE DATABASE IF NOT EXISTS chargingstationdb;
USE chargingstationdb;

CREATE TABLE IF NOT EXISTS chargingstation (
  charger_id INT AUTO_INCREMENT PRIMARY KEY,
  charger_name VARCHAR(30) NOT NULL,
  charger_location VARCHAR(100) NOT NULL,
  latitude DOUBLE PRECISION NOT NULL,
  longitude DOUBLE PRECISION NOT NULL,
  status VARCHAR(10) NOT NULL DEFAULT 'UP',
  charger_image TEXT,  -- Add charger_image field
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- INSERT DUMMY DATA
INSERT INTO chargingstation (charger_name, charger_location, latitude, longitude, status, charger_image)
VALUES
  ('Station A', 'Location A', 1.3550, 103.8257, 'UP', 'charger_dummy.jpg'),  -- Approximately 1 km from Singapore center
  ('Station B', 'Location B', 1.3455, 103.8228, 'DOWN', 'charger_dummy.jpg'),  -- Approximately 2 km from Singapore center
  ('Station C', 'Location C', 1.3605, 103.8275, 'UP', 'charger_dummy.jpg');  -- Approximately 3 km from Singapore center

-- Bookings
-- Create ChargingStationBooking table
CREATE TABLE IF NOT EXISTS chargingstationbooking (
  booking_id INT AUTO_INCREMENT PRIMARY KEY,
  charger_id INT NOT NULL,
  user_id INT NOT NULL,
  booking_datetime DATETIME NOT NULL,
  booking_duration_hours INT NOT NULL,
  booking_status ENUM('IN_PROGRESS', 'CANCELLED', 'COMPLETED', 'EXCEEDED') DEFAULT 'IN_PROGRESS',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_chargingstation FOREIGN KEY (charger_id) REFERENCES chargingstation(charger_id)
);

-- Populate ChargingStationBooking with dummy data
INSERT INTO chargingstationbooking (charger_id, user_id, booking_datetime, booking_duration_hours, booking_status)
VALUES
  (1, 1, '2024-03-09 10:00:00', 2, 'IN_PROGRESS'),  -- Booking in progress
  (2, 2, '2024-03-10 15:00:00', 1, 'EXCEEDED'),     -- Booking exceeded
  (3, 3, '2024-03-11 12:00:00', 3, 'COMPLETED'),    -- Completed booking
  (1, 2, '2024-03-12 08:00:00', 1, 'CANCELLED');    -- Cancelled booking

-- CREATE TABLE IF NOT EXISTS chargingstationbooking (
--   booking_id INT AUTO_INCREMENT PRIMARY KEY,
--   charger_id INT,
--   user_id INT,
--   booking_date DATE NOT NULL,
--   booking_time_start TIME NOT NULL,
--   booking_duration_hours INT NOT NULL,
--   booking_status ENUM('IN_PROGRESS', 'CANCELLED', 'COMPLETED', 'EXCEEDED') DEFAULT 'IN_PROGRESS',
--   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--   CONSTRAINT fk_chargingstation FOREIGN KEY (charger_id) REFERENCES chargingstation(charger_id)
-- );

-- INSERT INTO chargingstationbooking (charger_id, user_id, booking_date, booking_time_start, booking_duration_hours, booking_status)
-- VALUES
--   (1, 1, '2024-03-09', '10:00:00', 2, 'IN_PROGRESS'),  -- Booking in progress
--   (2, 2, '2024-03-10', '15:00:00', 1, 'EXCEEDED'),  -- Booking exceeded
--   (3, 3, '2024-03-11', '12:00:00', 3, 'COMPLETED'),  -- Completed booking
--   (1, 2, '2024-03-12', '08:00:00', 1, 'CANCELLED');  -- Cancelled booking


-- FUNCTIONS
-- FUNCTIONS
DROP FUNCTION IF EXISTS check_booking_overlap;
DELIMITER //
CREATE FUNCTION check_booking_overlap(
    p_charger_id INT,
    p_booking_datetime DATETIME,
    p_booking_duration_hours INT
) RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE overlap_count INT;

    -- Check if there are any overlapping bookings for the given charger, date, and time
    SELECT COUNT(*)
    INTO overlap_count
    FROM chargingstationbooking
    WHERE charger_id = p_charger_id
	AND booking_status = 'IN_PROGRESS'
	AND (
		-- Case 1: New booking starts before existing booking and ends after existing booking
		(p_booking_datetime <= booking_datetime AND ADDTIME(p_booking_datetime, SEC_TO_TIME(p_booking_duration_hours * 3600)) > ADDTIME(booking_datetime, SEC_TO_TIME(booking_duration_hours * 3600)))
		OR
		-- Case 2: New booking starts after existing booking and ends before existing booking
		(p_booking_datetime >= booking_datetime AND ADDTIME(p_booking_datetime, SEC_TO_TIME(p_booking_duration_hours * 3600)) < ADDTIME(booking_datetime, SEC_TO_TIME(booking_duration_hours * 3600)))
		OR
		-- Case 3: New booking starts before existing booking and ends before existing booking
		(p_booking_datetime <= booking_datetime AND ADDTIME(p_booking_datetime, SEC_TO_TIME(p_booking_duration_hours * 3600)) > booking_datetime)
		OR
		-- Case 4: New booking starts after existing booking and ends after existing booking
		(p_booking_datetime >= booking_datetime AND ADDTIME(p_booking_datetime, SEC_TO_TIME(p_booking_duration_hours * 3600)) < ADDTIME(booking_datetime, SEC_TO_TIME(booking_duration_hours * 3600)))
	);

    -- If there are overlapping bookings, return true; otherwise, return false
    IF overlap_count > 0 THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END //
DELIMITER ;

-- DROP FUNCTION IF EXISTS check_booking_overlap;
-- DELIMITER //
-- CREATE FUNCTION check_booking_overlap(
--     p_charger_id INT,
--     p_booking_date DATE,
--     p_booking_time_start TIME,
--     p_booking_duration_hours INT
-- ) RETURNS BOOLEAN
-- DETERMINISTIC
-- BEGIN
--     DECLARE overlap_count INT;

--     -- Check if there are any overlapping bookings for the given charger, date, and time
--     SELECT COUNT(*)
--     INTO overlap_count
--     FROM chargingstationbooking
--     WHERE charger_id = p_charger_id
--     AND booking_date = p_booking_date
-- 	AND booking_status = 'IN_PROGRESS'
-- 	AND (
-- 		-- Case 1: New booking starts before existing booking and ends after existing booking
-- 		(p_booking_time_start <= booking_time_start AND ADDTIME(p_booking_time_start, SEC_TO_TIME(p_booking_duration_hours * 3600)) > ADDTIME(booking_time_start, SEC_TO_TIME(booking_duration_hours * 3600)))
-- 		OR
-- 		-- Case 2: New booking starts after existing booking and ends before existing booking
-- 		(p_booking_time_start >= booking_time_start AND ADDTIME(p_booking_time_start, SEC_TO_TIME(p_booking_duration_hours * 3600)) < ADDTIME(booking_time_start, SEC_TO_TIME(booking_duration_hours * 3600)))
-- 		OR
-- 		-- Case 3: New booking starts before existing booking and ends before existing booking
-- 		(p_booking_time_start <= booking_time_start AND ADDTIME(p_booking_time_start, SEC_TO_TIME(p_booking_duration_hours * 3600)) > booking_time_start)
-- 		OR
-- 		-- Case 4: New booking starts after existing booking and ends after existing booking
-- 		(p_booking_time_start >= booking_time_start AND ADDTIME(p_booking_time_start, SEC_TO_TIME(p_booking_duration_hours * 3600)) < ADDTIME(booking_time_start, SEC_TO_TIME(booking_duration_hours * 3600)))
-- 	);

--     -- If there are overlapping bookings, return true; otherwise, return false
--     IF overlap_count > 0 THEN
--         RETURN TRUE;
--     ELSE
--         RETURN FALSE;
--     END IF;
-- END //
-- DELIMITER ;