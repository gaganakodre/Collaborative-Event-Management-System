-- users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role_id INT REFERENCES roles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- roles table
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

alter table roles add column deactivation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;


INSERT INTO roles (name, description) VALUES 
('Owner', 'Has full control over resources, including managing users and permissions.'),
('Editor', 'Can create, update, and delete content but cannot manage users or system settings.'),
('Viewer', 'Can only view content but cannot make changes.');