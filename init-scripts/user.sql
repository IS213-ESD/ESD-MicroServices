CREATE DATABASE IF NOT EXISTS userdb;
USE userdb;
--   user_id VARCHAR(100) NOT NULL PRIMARY KEY,

CREATE TABLE IF NOT EXISTS user (
  user_id VARCHAR(30) PRIMARY KEY,
  email VARCHAR(50) NOT NULL,
  homeaddress VARCHAR(100),
  phone VARCHAR(8),
  username VARCHAR(30),
  payment_token VARCHAR(50)
);

INSERT INTO user (user_id, email, homeaddress, phone, username, payment_token) VALUES ('1', 'john@example.com', '123 Main St', '90776123', 'john123', 'abc123'), ('2', 'jane@example.com', '456 Elm St', '90776123', 'jane456', 'def456'), ('3', 'bob@example.com', '789 Oak St', '90776123', 'bob789', 'ghi789');


