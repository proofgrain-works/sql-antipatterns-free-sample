-- SPDX-License-Identifier: MIT
CREATE TABLE payments (id INTEGER PRIMARY KEY, amount_cents INTEGER NOT NULL);
CREATE INDEX idx_payments_amount ON payments(amount_cents);
INSERT INTO payments VALUES (1,4999),(2,5000),(3,5050),(4,5099),(5,5100),(6,12000);
