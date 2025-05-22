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


-- events table
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    user_id INT REFERENCES users(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE events ADD COLUMN recurrence_rule TEXT;


CREATE TABLE event_permissions (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('view', 'edit', 'owner')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (event_id, user_id)
);



CREATE TABLE event_versions (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    title TEXT,
    description TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    recurrence_rule TEXT,
    updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    change_summary TEXT,
    UNIQUE (event_id, version_number)
);

CREATE TABLE event_changelog (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    action TEXT NOT NULL CHECK (action IN ('create', 'update', 'delete')),
    user_id INTEGER NOT NULL REFERENCES users(id),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE event_version_diffs (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    diff_summary TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);



CREATE OR REPLACE FUNCTION rollback_event_to_version(event_id INT, version_id INT)
RETURNS void AS $$
DECLARE
    version_record event_versions%ROWTYPE;
BEGIN
    SELECT * INTO version_record
    FROM event_versions
    WHERE event_id = event_id AND id = version_id;

    UPDATE events
    SET title = version_record.title,
        description = version_record.description,
        start_time = version_record.start_time,
        end_time = version_record.end_time,
        recurrence_rule = version_record.recurrence_rule
    WHERE id = event_id;
$$ LANGUAGE plpgsql;
