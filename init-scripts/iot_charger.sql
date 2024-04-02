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
  (2,'Vacant'), 
  (3,'Vacant'); 