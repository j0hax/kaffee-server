CREATE TABLE IF NOT EXISTS users (
    name varchar(255),
    balance int,
    drink_count int,
    last_update int,
    transponder_hash varchar(255)
);

CREATE TABLE IF NOT EXISTS clients (
    api_key varchar(255)
);
