-- SPDX-License-Identifier: MIT
CREATE TABLE employees (employee_id INTEGER PRIMARY KEY, employee_name TEXT NOT NULL, status TEXT NOT NULL);
CREATE TABLE badges (badge_id INTEGER PRIMARY KEY, employee_id INTEGER NOT NULL, status TEXT NOT NULL);
INSERT INTO employees VALUES (1,'Aki','active'),(2,'Mio','active'),(3,'Ren','inactive');
INSERT INTO badges VALUES (101,1,'issued'),(102,2,'revoked'),(103,3,'inactive');
