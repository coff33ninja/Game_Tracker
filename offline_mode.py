# offline_mode.py
from db_manager import DBManager
import json


class OfflineMode:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager

    def cache_games(self, filename="games_cache.json"):
        games = []
        for status in ["active", "claimed", "owned", "expired"]:
            games.extend(
                [
                    {"status": status, "platform": g[0], "title": g[1], "detail": g[2]}
                    for g in self.db.get_games_by_status(status)
                ]
            )
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(games, f, indent=2)

    def load_cache(self, filename="games_cache.json"):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
