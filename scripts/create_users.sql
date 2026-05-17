-- Tabla de usuarios del panel de administración (TintWrap)
-- Ejecutar en MySQL: USE tintwrap;

CREATE TABLE IF NOT EXISTS users (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  email VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL,
  full_name VARCHAR(255) NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  last_login_at DATETIME NULL,
  added_date DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  updated_date DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Usuario inicial: al arrancar el backend con la tabla vacía se crea con .env:
--   ADMIN_EMAIL=admin@tintwrap.com
--   ADMIN_PASSWORD=admin123
--
-- Para insertar manualmente, genera el hash bcrypt:
--   python -c "import bcrypt; print(bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode())"
--
-- INSERT INTO users (email, password, full_name, is_active)
-- VALUES ('admin@tintwrap.com', '<hash_bcrypt>', 'Administrador', 1);
