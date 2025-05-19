# game_filter.py
from db_manager import DBManager
from typing import List, Tuple, Optional
import sqlite3

class GameFilter:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager

    def filter_games(self, status: str, platform: Optional[str] = None, genre: Optional[str] = None, search_term: Optional[str] = None) -> List[Tuple[Optional[str], Optional[str], Optional[str]]]:
        query = f"SELECT platform, title, {'end_date' if status == 'active' else 'claim_date' if status == 'claimed' else 'epitaph' if status == 'expired' else 'acquisition_date'} FROM games WHERE status = ?"
        params = [status]
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        if genre:
            query += " AND genre LIKE ?"
            params.append(f"%{genre}%")
        if search_term:
            query += " AND title LIKE ?"
            params.append(f"%{search_term}%")
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
