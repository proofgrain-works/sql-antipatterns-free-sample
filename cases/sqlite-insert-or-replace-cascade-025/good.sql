-- SPDX-License-Identifier: MIT
INSERT INTO good_users (id,email,name) VALUES (2,'a@example.test','Akira') ON CONFLICT(email) DO UPDATE SET name=excluded.name;
