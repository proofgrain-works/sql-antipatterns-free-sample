-- SPDX-License-Identifier: MIT
SELECT id FROM payments WHERE amount_cents / 100 = 50 ORDER BY id;
