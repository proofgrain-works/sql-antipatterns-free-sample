-- SPDX-License-Identifier: MIT
SELECT id FROM payments WHERE amount_cents >= 5000 AND amount_cents < 5100 ORDER BY id;
