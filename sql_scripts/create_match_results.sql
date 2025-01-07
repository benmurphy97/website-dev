CREATE TABLE match_results (
  match_date DATE,
  season VARCHAR(10),
  competition VARCHAR(15)
  home_team VARCHAR(20),
  away_team VARCHAR(20),
  home_score INTEGER,
  away_score INTEGER
);


SELECT * FROM match_results

-- insert single row
INSERT INTO match_results
VALUES ('2021-09-04', 'BIARRITZ', 'BORDEAUX', 27, 15);

-- delete everything from table
DELETE FROM match_results