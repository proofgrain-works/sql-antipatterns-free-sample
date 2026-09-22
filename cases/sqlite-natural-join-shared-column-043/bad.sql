-- SPDX-License-Identifier: MIT
SELECT employee_id, employee_name, badge_id FROM employees NATURAL JOIN badges ORDER BY employee_id;
