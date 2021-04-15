CREATE TABLE IF NOT EXISTS users (
    name varchar(255),
    balance int,
    drink_count int,
    last_update int,
    transponder_hash varchar(255)
);


CREATE TABLE IF NOT EXISTS clients (
    api_key varchar(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS admins (
    username varchar(255) NOT NULL UNIQUE,
    pw_hash char(60) NOT NULL
);

-- DEFAULT: user admin, password Barista*1
INSERT OR IGNORE INTO admins VALUES ('admin', '$2b$12$gjItohiilKXnFYDxEpA1X.dZnHjk5tEoKQnSss90JWDaeTDAMkHGa');