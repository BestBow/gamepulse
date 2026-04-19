import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ── DB connection ────────────────────────────────────────────
connection_url = URL.create(
    drivername = "postgresql+psycopg2",
    username   = os.getenv('DB_USER'),
    password   = os.getenv('DB_PASSWORD'),
    host       = os.getenv('DB_HOST'),
    port       = int(os.getenv('DB_PORT', 5432)),
    database   = os.getenv('DB_NAME'),
)
engine = create_engine(connection_url)

def query(sql, params=None):
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        cols   = result.keys()
        return [dict(zip(cols, row)) for row in result]

# ── Routes ───────────────────────────────────────────────────

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'GamePulse API running'})

@app.route('/api/stats')
def stats():
    data = query("""
        SELECT
            (SELECT COUNT(*) FROM games)     AS total_games,
            (SELECT COUNT(*) FROM genres)    AS total_genres,
            (SELECT COUNT(*) FROM platforms) AS total_platforms,
            (SELECT ROUND(AVG(rating)::numeric, 2) FROM games
             WHERE rating > 0)               AS avg_rating,
            (SELECT ROUND(AVG(metacritic)::numeric, 1) FROM games
             WHERE metacritic IS NOT NULL)   AS avg_metacritic
    """)
    return jsonify(data[0])

@app.route('/api/games')
def games():
    limit  = request.args.get('limit',  20,  type=int)
    offset = request.args.get('offset', 0,   type=int)
    genre  = request.args.get('genre',  None)
    order  = request.args.get('order',  'rating')

    allowed_orders = {'rating', 'metacritic', 'released', 'playtime'}
    if order not in allowed_orders:
        order = 'rating'

    if genre:
        sql = """
            SELECT g.id, g.name, g.rating, g.metacritic,
                   g.released, g.playtime, g.rating_count
            FROM games g
            JOIN game_genres gg ON g.id = gg.game_id
            JOIN genres ge      ON gg.genre_id = ge.id
            WHERE LOWER(ge.name) = LOWER(:genre)
              AND g.rating > 0
            ORDER BY g.""" + order + """ DESC NULLS LAST
            LIMIT :limit OFFSET :offset
        """
        rows = query(sql, {'genre': genre, 'limit': limit, 'offset': offset})
    else:
        sql = """
            SELECT id, name, rating, metacritic,
                   released, playtime, rating_count
            FROM games
            WHERE rating > 0
            ORDER BY """ + order + """ DESC NULLS LAST
            LIMIT :limit OFFSET :offset
        """
        rows = query(sql, {'limit': limit, 'offset': offset})

    for row in rows:
        if row.get('released'):
            row['released'] = str(row['released'])
        if row.get('rating'):
            row['rating'] = float(row['rating'])

    return jsonify(rows)

@app.route('/api/genres')
def genres():
    rows = query("SELECT * FROM genre_stats ORDER BY game_count DESC")
    for row in rows:
        if row.get('avg_rating'):
            row['avg_rating'] = float(row['avg_rating'])
        if row.get('avg_metacritic'):
            row['avg_metacritic'] = float(row['avg_metacritic'])
    return jsonify(rows)

@app.route('/api/platforms')
def platforms():
    rows = query("""
        SELECT * FROM platform_stats
        ORDER BY game_count DESC
        LIMIT 15
    """)
    for row in rows:
        if row.get('avg_rating'):
            row['avg_rating'] = float(row['avg_rating'])
    return jsonify(rows)

@app.route('/api/yearly')
def yearly():
    rows = query("""
        SELECT * FROM yearly_releases
        WHERE release_year >= 1990
          AND release_year <= 2024
        ORDER BY release_year
    """)
    for row in rows:
        if row.get('release_year'):
            row['release_year'] = int(row['release_year'])
        if row.get('avg_rating'):
            row['avg_rating'] = float(row['avg_rating'])
    return jsonify(rows)

@app.route('/api/rating-distribution')
def rating_distribution():
    rows = query("""
        SELECT
            CASE
                WHEN rating >= 4.5 THEN '4.5 - 5.0'
                WHEN rating >= 4.0 THEN '4.0 - 4.5'
                WHEN rating >= 3.5 THEN '3.5 - 4.0'
                WHEN rating >= 3.0 THEN '3.0 - 3.5'
                WHEN rating >= 2.0 THEN '2.0 - 3.0'
                ELSE 'Below 2.0'
            END AS rating_range,
            COUNT(*) AS game_count
        FROM games
        WHERE rating > 0
        GROUP BY rating_range
        ORDER BY MIN(rating) DESC
    """)
    return jsonify(rows)

if __name__ == '__main__':
    app.run(debug=True, port=5001)