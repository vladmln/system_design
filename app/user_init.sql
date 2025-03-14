CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    is_admin BOOLEAN DEFAULT false
);

CREATE INDEX IF NOT EXISTS idx_username ON users(username);

INSERT INTO users (username, password_hash, is_admin)
VALUES ('admin', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', true)
ON CONFLICT (username) DO NOTHING;