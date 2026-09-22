-- SPDX-License-Identifier: MIT
CREATE TABLE teams (id INTEGER PRIMARY KEY, department TEXT NOT NULL);
CREATE TABLE scores (id INTEGER PRIMARY KEY, team_id INTEGER NOT NULL, score REAL NOT NULL);
INSERT INTO teams VALUES (1,'Sales'),(2,'Sales'),(3,'Support');
INSERT INTO scores VALUES (11,1,100),(12,2,50),(13,2,50),(14,2,50),(15,3,80),(16,3,60);
