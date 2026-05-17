-- Ejecutar en MySQL (base tintwrap) si hay error 500 al crear servicios.

ALTER TABLE services
  MODIFY id INT NOT NULL AUTO_INCREMENT,
  MODIFY description LONGTEXT NULL;

ALTER TABLE service_galleries
  MODIFY id INT NOT NULL AUTO_INCREMENT,
  MODIFY title VARCHAR(255) NULL,
  MODIFY file1 LONGTEXT NULL,
  MODIFY file2 LONGTEXT NULL;

CREATE TABLE IF NOT EXISTS configurations (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  site_title VARCHAR(255) NOT NULL DEFAULT 'TintWrap',
  meta_title VARCHAR(255) NULL,
  meta_description TEXT NULL,
  youtube_url VARCHAR(512) NULL,
  tiktok_url VARCHAR(512) NULL,
  instagram_url VARCHAR(512) NULL,
  facebook_url VARCHAR(512) NULL,
  phone VARCHAR(64) NULL,
  contact_email VARCHAR(255) NULL,
  address TEXT NULL,
  whatsapp_url VARCHAR(512) NULL,
  added_date DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  updated_date DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
