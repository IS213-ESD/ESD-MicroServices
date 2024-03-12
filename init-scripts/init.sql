SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+08:00";

-- Grant privileges to the user on all database
GRANT ALL PRIVILEGES ON *.* TO 'user'@'%'; -- Charging Station

-- Flush privileges to apply changes
FLUSH PRIVILEGES;