-- Agrismart Database Initialization Script
-- This script creates the initial database structure and sample data

-- Create database if it doesn't exist
-- CREATE DATABASE agrismart_db;

-- Connect to the database
-- \c agrismart_db;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    email VARCHAR(120) UNIQUE NOT NULL,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    location VARCHAR(100),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Create predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    nitrogen DOUBLE PRECISION NOT NULL,
    phosphorus DOUBLE PRECISION NOT NULL,
    potassium DOUBLE PRECISION NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    humidity DOUBLE PRECISION NOT NULL,
    ph DOUBLE PRECISION NOT NULL,
    rainfall DOUBLE PRECISION NOT NULL,
    predicted_crop VARCHAR(100) NOT NULL,
    confidence_score DOUBLE PRECISION NOT NULL,
    alternative_crops JSONB,
    model_version VARCHAR(20) DEFAULT 'v1.0',
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    location_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT
);

-- Create weather_requests table
CREATE TABLE IF NOT EXISTS weather_requests (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    location_name VARCHAR(100),
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    rainfall DOUBLE PRECISION,
    description VARCHAR(100),
    icon VARCHAR(10),
    data_source VARCHAR(50),
    api_status VARCHAR(20),
    response_time DOUBLE PRECISION,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT
);

-- Create model_performance table
CREATE TABLE IF NOT EXISTS model_performance (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    model_version VARCHAR(20) NOT NULL,
    model_type VARCHAR(50) DEFAULT 'RandomForest',
    accuracy DOUBLE PRECISION,
    precision DOUBLE PRECISION,
    recall DOUBLE PRECISION,
    f1_score DOUBLE PRECISION,
    confusion_matrix JSONB,
    training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    training_duration DOUBLE PRECISION,
    dataset_size INTEGER,
    features_used JSONB,
    model_file_path VARCHAR(255),
    model_file_size INTEGER,
    scaler_file_path VARCHAR(255)
);

-- Create user_sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_type VARCHAR(20),
    browser VARCHAR(50),
    os VARCHAR(50),
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    duration DOUBLE PRECISION,
    page_views INTEGER DEFAULT 0,
    predictions_made INTEGER DEFAULT 0,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    country VARCHAR(100),
    city VARCHAR(100)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_predictions_user_id ON predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at);
CREATE INDEX IF NOT EXISTS idx_weather_requests_user_id ON weather_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_weather_requests_created_at ON weather_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for users table
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample admin user (password: admin123)
INSERT INTO users (email, username, password_hash, first_name, last_name, role, is_verified, is_active)
VALUES (
    'admin@agrismart.com',
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK8y', -- admin123
    'Admin',
    'User',
    'admin',
    TRUE,
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Insert sample regular user (password: user123)
INSERT INTO users (email, username, password_hash, first_name, last_name, role, is_verified, is_active)
VALUES (
    'user@agrismart.com',
    'demo_user',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK8y', -- user123
    'Demo',
    'User',
    'user',
    TRUE,
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO agrismart_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO agrismart_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO agrismart_user;

-- Create views for analytics
CREATE OR REPLACE VIEW user_analytics AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.created_at,
    COUNT(p.id) as total_predictions,
    COUNT(wr.id) as total_weather_requests,
    AVG(p.confidence_score) as avg_confidence,
    MAX(p.created_at) as last_prediction
FROM users u
LEFT JOIN predictions p ON u.id = p.user_id
LEFT JOIN weather_requests wr ON u.id = wr.user_id
GROUP BY u.id, u.username, u.email, u.created_at;

-- Create view for prediction statistics
CREATE OR REPLACE VIEW prediction_stats AS
SELECT 
    predicted_crop,
    COUNT(*) as count,
    AVG(confidence_score) as avg_confidence,
    MIN(confidence_score) as min_confidence,
    MAX(confidence_score) as max_confidence
FROM predictions
GROUP BY predicted_crop
ORDER BY count DESC;

-- Grant permissions on views
GRANT SELECT ON user_analytics TO agrismart_user;
GRANT SELECT ON prediction_stats TO agrismart_user;

-- Print completion message
DO $$
BEGIN
    RAISE NOTICE 'Agrismart database initialization completed successfully!';
    RAISE NOTICE 'Sample users created:';
    RAISE NOTICE 'Admin: admin@agrismart.com / admin123';
    RAISE NOTICE 'User: user@agrismart.com / user123';
END $$;
