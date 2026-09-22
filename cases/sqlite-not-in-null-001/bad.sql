-- SPDX-License-Identifier: MIT
SELECT id, name FROM customers WHERE id NOT IN (SELECT customer_id FROM orders) ORDER BY id;
