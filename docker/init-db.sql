-- Initialize APK Threat Detection Database

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Insert test user (change password in production!)
INSERT INTO users (id, username, email, hashed_password, is_admin)
VALUES (
    'user-001',
    'admin',
    'admin@apkthreat.local',
    '$2b$12$UZfDg6XwzVfX3h8RhGKBR.LKj7KBl3l5Z3D8K9Ll4E3m5F6G7H8I9J0K',
    true
)
ON CONFLICT (username) DO NOTHING;

-- Grant permissions on apk_threat database
GRANT USAGE ON SCHEMA public TO apk_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO apk_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO apk_user;

-- Ensure tables created by the backend app via SQLAlchemy are accessible to apk_user
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO apk_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO apk_user;
