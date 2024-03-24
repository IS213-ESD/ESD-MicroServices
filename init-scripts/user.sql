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




