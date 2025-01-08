CREATE TABLE matches_raw (
  match_date DATE,
  season VARCHAR(10),
  league VARCHAR(15),
  home_team VARCHAR(20),
  away_team VARCHAR(20),
  match_link VARCHAR(100),

  match_result VARCHAR(20),
  home_score INTEGER,
  away_score INTEGER,
  match_result_class INTEGER,
  
  home_n_tries INTEGER,
  away_n_tries INTEGER,
  home_n_conversions INTEGER,
  away_n_conversions INTEGER,
  home_n_pen_kicks INTEGER,
  away_n_pen_kicks INTEGER,
  home_n_pen_tries INTEGER,
  away_n_pen_tries INTEGER
  
);


DELETE FROM matches_raw;
DROP TABLE matches_raw;


SELECT * FROM matches_raw
ORDER BY match_date