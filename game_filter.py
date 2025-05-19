# game_filter.py
from db_manager import DBManager
from typing import List, Tuple, Optional
import sqlite3

class GameFilter:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager

    def filter_games(self, status: str, platform: Optional[str] = None, genre: Optional[str] = None, search_term: Optional[str] = None) -> List[Tuple[Optional[str], Optional[str], Optional[str]]]:
        # Determine the correct date/detail column based on status
        detail_column = 'end_date' # Default for active
        if status == 'claimed':
            detail_column = 'claim_date'
        elif status == 'expired':
            detail_column = 'epitaph'
        elif status == 'owned': # Though 'owned' status is usually handled differently for display
            detail_column = 'acquisition_date'

        query = f"SELECT platform, title, {detail_column} FROM games WHERE status = ?"
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

        if status == "active":
            # Ensure active games listed are not already in the owned 'Trophy Case'
            query += " AND NOT EXISTS (SELECT 1 FROM games g2 WHERE g2.title = games.title AND g2.platform = games.platform AND g2.status = 'owned')"

        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
