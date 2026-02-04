CREATE TABLE IF NOT EXISTS `device_status` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `device_id` CHAR(20) NOT NULL,
  `status` ENUM('RUNNING', 'IDLE', 'ALARM', 'MAINTENANCE', 'OFFLINE') NOT NULL DEFAULT 'OFFLINE',
  `current_x` DECIMAL(10, 3) NULL,
  `current_y` DECIMAL(10, 3) NULL,
  `current_z` DECIMAL(10, 3) NULL,
  `spindle_speed` DECIMAL(10, 2) NULL,
  `feed_rate` DECIMAL(10, 2) NULL,
  `load_percent` DECIMAL(5, 2) NULL,
  `alarm_code` VARCHAR(50) NULL,
  `alarm_message` VARCHAR(255) NULL,
  `recorded_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_device_id` (`device_id`),
  INDEX `idx_recorded_at` (`recorded_at`),
  INDEX `idx_device_time` (`device_id`, `recorded_at`),
  CONSTRAINT `fk_device_status_machine` FOREIGN KEY (`device_id`) REFERENCES `machines` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;