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

-- INSERT DUMMY DATA
INSERT INTO user (user_id, email, homeaddress, phone, username, payment_token)
VALUES
  ("NVqPLXexIFUr3loYRl1GJgkfAep2", "testuser@gmail.com", "", "83217652", "Bob", "cus_Pqexqy3LNhmwzf:pm_1P0xd603o249Di9WnXIY52wQ");




