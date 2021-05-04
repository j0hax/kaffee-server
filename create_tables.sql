-- User database
CREATE TABLE IF NOT EXISTS users (
    name varchar(255) NOT NULL,
    last_update FLOAT DEFAULT (strftime('%s','now')),
    transponder_hash varchar(255)
);

CREATE TRIGGER IF NOT EXISTS update_last_update
    AFTER UPDATE
    ON users
    BEGIN
    UPDATE users SET last_update = strftime('%s','now') WHERE rowid = old.rowid;
    END;

-- Transactions from users
CREATE TABLE IF NOT EXISTS transactions (
    user INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    description varchar(255),
    timestamp FLOAT DEFAULT (strftime('%s','now'))
);

-- Clients which need an API Key to log in
CREATE TABLE IF NOT EXISTS clients (
    api_key varchar(255) NOT NULL UNIQUE
);

-- View which calculates balances from transactions
DROP VIEW IF EXISTS balances;
CREATE VIEW balances AS
    SELECT users.rowid AS id,
    sum(CASE WHEN transactions.amount > 0 THEN 1 ELSE 0 END) AS deposit_count,
    sum(CASE WHEN transactions.amount > 0 THEN transactions.amount ELSE 0 END) AS deposits,
    sum(CASE WHEN transactions.amount < 0 THEN 1 ELSE 0 END) AS withdrawal_count,
    sum(CASE WHEN transactions.amount < 0 THEN transactions.amount ELSE 0 END) AS withdrawals,
    SUM(transactions.amount) AS balance FROM transactions
    INNER JOIN users ON transactions.user = users.rowid GROUP BY users.rowid;

-- Admins allowed to log and administer 
CREATE TABLE IF NOT EXISTS admins (
    username varchar(255) NOT NULL UNIQUE,
    pw_hash char(60) NOT NULL
);

-- DEFAULT Admin account: user admin, password Barista*1
INSERT OR IGNORE INTO admins VALUES ('admin', '$2b$12$gjItohiilKXnFYDxEpA1X.dZnHjk5tEoKQnSss90JWDaeTDAMkHGa');

-- DEFAULT API Key: ugabNkEtmjCwZeb69BrO4L1sHhgQY/X6 (use 'cat /dev/random | base64 | head -c 32' to generate a new one)
INSERT OR IGNORE into clients VALUES ('ugabNkEtmjCwZeb69BrO4L1sHhgQY/X6');
