import os
import time
import requests
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from sqlalchemy.engine import URL
load_dotenv()

# ── Config ───────────────────────────────────────────────────
API_KEY  = os.getenv('RAWG_API_KEY')
connection_url = URL.create(
    drivername = "postgresql+psycopg2",
    username   = os.getenv('DB_USER'),
    password   = os.getenv('DB_PASSWORD'),
    host       = os.getenv('DB_HOST'),
    port       = int(os.getenv('DB_PORT', 5432)),
    database   = os.getenv('DB_NAME'),
)
engine = create_engine(connection_url)

BASE_URL  = 'https://api.rawg.io/api'
PAGES     = 20
PAGE_SIZE = 40

# ── Extract ──────────────────────────────────────────────────
def fetch_games(pages=PAGES):
    all_games = []
    print(f"Fetching {pages} pages of games from RAWG API...")

    for page in range(1, pages + 1):
        url = f"{BASE_URL}/games"
        params = {
            'key':       API_KEY,
            'page':      page,
            'page_size': PAGE_SIZE,
            'ordering':  '-rating',
            'metacritic': '1,100',
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            all_games.extend(data.get('results', []))
            print(f"  Page {page}/{pages} — {len(data.get('results', []))} games fetched")
            time.sleep(0.25)   # respect rate limit
        except requests.RequestException as e:
            print(f"  Error on page {page}: {e}")
            continue

    print(f"Total games fetched: {len(all_games)}")
    return all_games

# ── Transform ────────────────────────────────────────────────
def transform_games(raw_games):
    games, genres, platforms, game_genres, game_platforms = [], [], [], [], []

    seen_genres    = {}
    seen_platforms = {}

    for g in raw_games:
        game_id = g.get('id')
        if not game_id:
            continue

        # Game record
        games.append({
            'id':           game_id,
            'name':         g.get('name', ''),
            'released':     g.get('released'),
            'rating':       g.get('rating'),
            'rating_count': g.get('ratings_count'),
            'metacritic':   g.get('metacritic'),
            'playtime':     g.get('playtime'),
            'updated':      g.get('updated'),
        })

        # Genres
        for genre in g.get('genres', []):
            gid = genre.get('id')
            if gid and gid not in seen_genres:
                seen_genres[gid] = True
                genres.append({
                    'id':   gid,
                    'name': genre.get('name'),
                    'slug': genre.get('slug'),
                })
            if gid:
                game_genres.append({'game_id': game_id, 'genre_id': gid})

        # Platforms
        for p in g.get('platforms', []):
            plat = p.get('platform', {})
            pid  = plat.get('id')
            if pid and pid not in seen_platforms:
                seen_platforms[pid] = True
                platforms.append({
                    'id':   pid,
                    'name': plat.get('name'),
                    'slug': plat.get('slug'),
                })
            if pid:
                game_platforms.append({'game_id': game_id, 'platform_id': pid})

    return (
        pd.DataFrame(games).drop_duplicates('id'),
        pd.DataFrame(genres).drop_duplicates('id'),
        pd.DataFrame(platforms).drop_duplicates('id'),
        pd.DataFrame(game_genres).drop_duplicates(),
        pd.DataFrame(game_platforms).drop_duplicates(),
    )

# ── Load ─────────────────────────────────────────────────────
def load_to_db(games_df, genres_df, platforms_df,
               game_genres_df, game_platforms_df):
    with engine.begin() as conn:
        # Clear junction tables first to avoid FK conflicts
        conn.execute(text("DELETE FROM game_genres"))
        conn.execute(text("DELETE FROM game_platforms"))
        conn.execute(text("DELETE FROM games"))
        conn.execute(text("DELETE FROM genres"))
        conn.execute(text("DELETE FROM platforms"))
        print("Cleared existing data.")

    # Load in dependency order
    games_df.to_sql('games',     engine, if_exists='append', index=False)
    genres_df.to_sql('genres',   engine, if_exists='append', index=False)
    platforms_df.to_sql('platforms', engine, if_exists='append', index=False)
    game_genres_df.to_sql('game_genres',     engine,
                           if_exists='append', index=False)
    game_platforms_df.to_sql('game_platforms', engine,
                              if_exists='append', index=False)

    print(f"Loaded: {len(games_df)} games, {len(genres_df)} genres, "
          f"{len(platforms_df)} platforms")

# ── Run pipeline ─────────────────────────────────────────────
def run():
    print(f"\n{'='*50}")
    print(f"  GamePulse ETL Pipeline — {datetime.now():%Y-%m-%d %H:%M}")
    print(f"{'='*50}")

    raw   = fetch_games()
    games, genres, platforms, gg, gp = transform_games(raw)
    load_to_db(games, genres, platforms, gg, gp)

    print("\nVerifying row counts...")
    with engine.connect() as conn:
        for table in ['games', 'genres', 'platforms',
                      'game_genres', 'game_platforms']:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  {table:<20} {count:>6} rows")

    print("\nETL complete.")

if __name__ == '__main__':
    run()