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

insert into users (name, balance, drink_count, last_update, transponder_hash) values ("Johannes Arnold", 9000, 30, strftime('%s', 'now')*1000, "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08");

INSERT INTO clients (api_key) VALUES ("ugabNkEtmjCwZeb69BrO4L1sHhgQY/X6");
