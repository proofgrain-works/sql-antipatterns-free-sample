-- SPDX-License-Identifier: MIT
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER);
INSERT INTO customers (id, name) VALUES (1, 'Aki'), (2, 'Beni'), (3, 'Chika');
INSERT INTO orders (id, customer_id) VALUES (101, 1), (102, NULL);
