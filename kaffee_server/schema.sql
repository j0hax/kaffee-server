-- User database
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vip INTEGER DEFAULT FALSE,
    name TEXT NOT NULL,
    last_update REAL DEFAULT (strftime('%s','now')),
    transponder_code TEXT UNIQUE
);

-- User ID 0 is a special system user
INSERT INTO users (id, name) VALUES (0, "System");

-- Transactions from users
CREATE TABLE transactions (
    user INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    description TEXT,
    timestamp REAL DEFAULT (strftime('%s','now')),
    FOREIGN KEY(user) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TRIGGER update_last_update
    AFTER INSERT
    ON transactions FOR EACH ROW
    BEGIN
        UPDATE users SET last_update = strftime('%s','now') WHERE users.id = new.user;
    END;

-- Clients which need an API Key to log in
CREATE TABLE clients (
    api_key TEXT NOT NULL UNIQUE
);

-- View which calculates balances from transactions
CREATE VIEW balances AS
    SELECT users.id,
    sum(CASE WHEN transactions.amount > 0 THEN 1 ELSE 0 END) AS deposit_count,
    sum(CASE WHEN transactions.amount > 0 THEN transactions.amount ELSE 0 END) AS deposits,
    sum(CASE WHEN transactions.amount < 0 THEN 1 ELSE 0 END) AS withdrawal_count,
    sum(CASE WHEN transactions.amount < 0 THEN transactions.amount ELSE 0 END) AS withdrawals,
    SUM(transactions.amount) AS balance FROM transactions
    INNER JOIN users ON transactions.user = users.id GROUP BY users.id ORDER BY users.last_update DESC;

-- Admins allowed to log and administer 
CREATE TABLE admins (
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

-- DEFAULT Admin account: user admin, password Barista*1
INSERT OR IGNORE INTO admins VALUES ('admin', 'pbkdf2:sha256:150000$M4VkxWNb$8c337287426498650e4fdb05a9783294e52bfd508de53d9000e3f77c06e378fe');

-- DEFAULT API Key: ugabNkEtmjCwZeb69BrO4L1sHhgQY/X6 (use 'cat /dev/random | base64 | head -c 32' to generate a new one)
INSERT OR IGNORE into clients VALUES ('ugabNkEtmjCwZeb69BrO4L1sHhgQY/X6');
