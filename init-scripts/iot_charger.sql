CREATE DATABASE IF NOT EXISTS iotchargerdb;
USE iotchargerdb;

CREATE TABLE IF NOT EXISTS iotcharger (
  iot_charger_id INT AUTO_INCREMENT PRIMARY KEY,
  charger_id INT NOT NULL,
  status VARCHAR(10) NOT NULL DEFAULT 'Vacant'
);

-- INSERT DUMMY DATA
INSERT INTO iotcharger (charger_id, status)
VALUES
  (1,'Vacant'), 
  (1,'Vacant'), 
  (2,'Vacant'); 


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