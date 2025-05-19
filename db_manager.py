# db_manager.py
import sqlite3
from datetime import datetime, timezone # Added timezone
import random

class DBManager:
    def __init__(self, db_path="free_games.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY,
                title TEXT,
                platform TEXT,
                url TEXT,
                end_date TEXT,
                status TEXT,
                claim_date TEXT,
                epitaph TEXT,
                acquisition_date TEXT,
                price REAL,
                genre TEXT,
                language TEXT,
                playtime INTEGER,
                UNIQUE(title, platform, status)
            )
        """)
        conn.commit()
        conn.close()

    def add_game(self, title, platform, url, end_date=None, status="active", language=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO games (title, platform, url, end_date, status, language) VALUES (?, ?, ?, ?, ?, ?)",
                (title, platform, url, end_date.isoformat() if end_date else None, status, language)
            )
        except sqlite3.IntegrityError:
            pass  # Skip duplicates
        conn.commit()
        conn.close()

    def mark_game_owned(self, title, platform, url="", acquisition_date=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, status FROM games WHERE title = ? AND platform = ?", (title, platform))
        result = cursor.fetchone()
        if result:
            game_id, status = result
            cursor.execute(
                "UPDATE games SET status = 'owned', acquisition_date = ?, url = ? WHERE id = ?",
                (acquisition_date or datetime.now().isoformat(), url, game_id)
            )
        else:
            cursor.execute(
                "INSERT INTO games (title, platform, url, status, acquisition_date) VALUES (?, ?, ?, ?, ?)",
                (title, platform, url, "owned", acquisition_date or datetime.now().isoformat())
            )
        conn.commit()
        conn.close()

    def mark_game_claimed(self, url, claim_date=None):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "UPDATE games SET status = 'claimed', claim_date = ? WHERE url = ?",
            (claim_date or datetime.now().isoformat(), url)
        )
        conn.commit()
        conn.close()

    def check_expirations(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now_utc = datetime.now(timezone.utc) # Get current time in UTC, aware

        cursor.execute("SELECT id, end_date FROM games WHERE status = 'active' AND end_date IS NOT NULL")
        for game_id, end_date_str in cursor.fetchall():
            try:
                game_end_date_obj = datetime.fromisoformat(end_date_str)
                # If the parsed datetime is naive, assume it's UTC and make it aware
                if game_end_date_obj.tzinfo is None or game_end_date_obj.tzinfo.utcoffset(game_end_date_obj) is None:
                    game_end_date_obj = game_end_date_obj.replace(tzinfo=timezone.utc)

                if game_end_date_obj < now_utc:
                    # Game has expired
                epitaph = random.choice([
                    "Game Over: Unclaimed!",
                    "Pixel Dust in the Wind...",
                    "Lost in the Digital Abyss.",
                    "No Respawn for This One!"
                ])
                cursor.execute(
                    "UPDATE games SET status = 'expired', epitaph = ? WHERE id = ?",
                    (epitaph, game_id)
                )
            except ValueError:
                print(f"Warning: Could not parse end_date string '{end_date_str}' for game ID {game_id}. Skipping expiration check for this game.")
        conn.commit()
        conn.close()

    def get_games_by_status(self, status):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if status == "active":
            cursor.execute("SELECT platform, title, url, end_date FROM games WHERE status = ?", (status,))
            return [(p, t, u, e) for p, t, u, e in cursor.fetchall()]
        elif status == "claimed":
            cursor.execute("SELECT platform, title, claim_date FROM games WHERE status = ?", (status,))
            return [(p, t, c) for p, t, c in cursor.fetchall()]
        elif status == "expired":
            cursor.execute("SELECT platform, title, epitaph FROM games WHERE status = ?", (status,))
            return [(p, t, e) for p, t, e in cursor.fetchall()]
        elif status == "owned":
            cursor.execute("SELECT platform, title, acquisition_date FROM games WHERE status = ?", (status,))
            return [(p, t, a) for p, t, a in cursor.fetchall()]
        conn.close()
        return []

    def get_status_counts(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM games GROUP BY status")
        counts = {status: count for status, count in cursor.fetchall()}
        conn.close()
        return counts
