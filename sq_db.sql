CREATE TABLE IF NOT EXISTS posts (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
name_car text NOT NULL,
price integer NOT NULL,
felling text NOT NULL,
time integer NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
email text NOT NULL,
psw text NOT NULL,
avatar BLOB NOT NULL,
time integer NOT NULL
);