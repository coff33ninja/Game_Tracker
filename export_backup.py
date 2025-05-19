# export_backup.py
import csv
import json
import sqlite3
from db_manager import DBManager


class ExportBackup:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager

    def export_to_csv(self, filename="games_export.csv"):
        games = []
        for status in ["active", "claimed", "owned", "expired"]:
            games.extend([(status, *g) for g in self.db.get_games_by_status(status)])
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Status", "Platform", "Title", "Detail", "Price", "Genre"])
            for game in games:
                status, platform, title, detail = game[:4]
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT price, genre FROM games WHERE title = ? AND platform = ?",
                    (title, platform),
                )
                price, genre = cursor.fetchone()
                conn.close()
                writer.writerow(
                    [status, platform, title, detail, price or "", genre or ""]
                )

    def export_to_json(self, filename="games_export.json"):
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
