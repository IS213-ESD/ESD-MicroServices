CREATE DATABASE IF NOT EXISTS chargingstationdb;
USE chargingstationdb;

CREATE TABLE IF NOT EXISTS chargingstation (
  charger_id INT AUTO_INCREMENT PRIMARY KEY,
  charger_name VARCHAR(30) NOT NULL,
  latitude DOUBLE PRECISION NOT NULL,
  longitude DOUBLE PRECISION NOT NULL,
  status VARCHAR(10) NOT NULL DEFAULT 'UP',
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- INSERT DUMMY DATA
INSERT INTO chargingstation (charger_name, latitude, longitude, status)
VALUES
  ('Station A', 37.7749, -122.4194, 'UP'),
  ('Station B', 34.0522, -118.2437, 'DOWN'),
  ('Station C', 40.7128, -74.0060, 'UP');