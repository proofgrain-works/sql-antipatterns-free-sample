-- SPDX-License-Identifier: MIT
SELECT e.employee_id, e.employee_name, b.badge_id FROM employees AS e JOIN badges AS b ON b.employee_id = e.employee_id ORDER BY e.employee_id;
