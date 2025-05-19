# owned_games.py
from db_manager import DBManager


class OwnedGames:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager

    def add_owned_game(self, title, platform, url="", acquisition_date=None):
        self.db.mark_game_owned(title, platform, url, acquisition_date)

    def get_owned_games(self):
        return self.db.get_games_by_status("owned")
