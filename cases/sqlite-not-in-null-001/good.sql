-- SPDX-License-Identifier: MIT
SELECT c.id, c.name FROM customers AS c WHERE NOT EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id = c.id) ORDER BY c.id;
