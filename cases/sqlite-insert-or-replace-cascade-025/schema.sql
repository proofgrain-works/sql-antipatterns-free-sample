-- SPDX-License-Identifier: MIT
PRAGMA foreign_keys = ON;
CREATE TABLE bad_users (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE, name TEXT NOT NULL);
CREATE TABLE bad_sessions (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES bad_users(id) ON DELETE CASCADE);
INSERT INTO bad_users VALUES (1,'a@example.test','Aki');
INSERT INTO bad_sessions VALUES (10,1);
INSERT OR REPLACE INTO bad_users (id,email,name) VALUES (2,'a@example.test','Akira');
CREATE TABLE good_users (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE, name TEXT NOT NULL);
CREATE TABLE good_sessions (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES good_users(id) ON DELETE CASCADE);
INSERT INTO good_users VALUES (1,'a@example.test','Aki');
INSERT INTO good_sessions VALUES (10,1);
INSERT INTO good_users (id,email,name) VALUES (2,'a@example.test','Akira') ON CONFLICT(email) DO UPDATE SET name=excluded.name;
