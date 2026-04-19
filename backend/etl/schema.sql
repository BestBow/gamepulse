-- Games table
CREATE TABLE IF NOT EXISTS games (
    id              INTEGER PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    released        DATE,
    rating          NUMERIC(3,2),
    rating_count    INTEGER,
    metacritic      INTEGER,
    playtime        INTEGER,
    updated         TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Genres table
CREATE TABLE IF NOT EXISTS genres (
    id      INTEGER PRIMARY KEY,
    name    VARCHAR(100) NOT NULL,
    slug    VARCHAR(100)
);

-- Platforms table
CREATE TABLE IF NOT EXISTS platforms (
    id      INTEGER PRIMARY KEY,
    name    VARCHAR(100) NOT NULL,
    slug    VARCHAR(100)
);

-- Junction table — games to genres (many to many)
CREATE TABLE IF NOT EXISTS game_genres (
    game_id     INTEGER REFERENCES games(id) ON DELETE CASCADE,
    genre_id    INTEGER REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, genre_id)
);

-- Junction table — games to platforms (many to many)
CREATE TABLE IF NOT EXISTS game_platforms (
    game_id     INTEGER REFERENCES games(id) ON DELETE CASCADE,
    platform_id INTEGER REFERENCES platforms(id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, platform_id)
);

-- Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_games_rating     ON games(rating DESC);
CREATE INDEX IF NOT EXISTS idx_games_released   ON games(released);
CREATE INDEX IF NOT EXISTS idx_games_metacritic ON games(metacritic DESC);

-- Analytics views
CREATE OR REPLACE VIEW genre_stats AS
SELECT
    g.name                          AS genre,
    COUNT(DISTINCT gg.game_id)      AS game_count,
    ROUND(AVG(gm.rating)::numeric, 2) AS avg_rating,
    ROUND(AVG(gm.metacritic)::numeric, 1) AS avg_metacritic
FROM genres g
JOIN game_genres gg ON g.id = gg.genre_id
JOIN games gm       ON gg.game_id = gm.id
GROUP BY g.name
ORDER BY game_count DESC;

CREATE OR REPLACE VIEW platform_stats AS
SELECT
    p.name                          AS platform,
    COUNT(DISTINCT gp.game_id)      AS game_count,
    ROUND(AVG(gm.rating)::numeric, 2) AS avg_rating
FROM platforms p
JOIN game_platforms gp ON p.id = gp.platform_id
JOIN games gm          ON gp.game_id = gm.id
GROUP BY p.name
ORDER BY game_count DESC;

CREATE OR REPLACE VIEW yearly_releases AS
SELECT
    EXTRACT(YEAR FROM released)     AS release_year,
    COUNT(*)                        AS game_count,
    ROUND(AVG(rating)::numeric, 2)  AS avg_rating
FROM games
WHERE released IS NOT NULL
GROUP BY release_year
ORDER BY release_year;