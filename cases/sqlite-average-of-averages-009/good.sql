-- SPDX-License-Identifier: MIT
SELECT t.department, AVG(s.score) AS department_avg FROM teams AS t JOIN scores AS s ON s.team_id = t.id GROUP BY t.department ORDER BY t.department;
