-- SPDX-License-Identifier: MIT
WITH team_averages AS (SELECT t.department, t.id AS team_id, AVG(s.score) AS team_avg FROM teams AS t JOIN scores AS s ON s.team_id = t.id GROUP BY t.department, t.id) SELECT department, AVG(team_avg) AS department_avg FROM team_averages GROUP BY department ORDER BY department;
