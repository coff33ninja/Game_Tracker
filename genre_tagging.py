# genre_tagging.py
from db_manager import DBManager
import sqlite3 # Import for database operations

class GenreTagging:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager

    def tag_game(self, title, description):
        # The AIModule's parse_text method no longer extracts genres.
        # It's now focused on "is_free" classification and providing embeddings.
        # Genre tagging would require a different approach:
        # 1. A dedicated multi-label classification model trained on game descriptions and genres.
        # 2. Keyword extraction from the description.
        # 3. Using an external API that provides genre information.
        # For now, this function will be a placeholder and not update genres via AI.
        # We will implement a simple keyword-based approach.

        found_genres = []
        if not description: # Handle cases where description might be None or empty
            print(f"No description provided for '{title}', cannot tag genres.")
            return ""

        description_lower = description.lower()

        # Simple keyword matching for genres
        if "rpg" in description_lower or "role-playing" in description_lower: found_genres.append("RPG")
        if "shooter" in description_lower: found_genres.append("Shooter")
        if "adventure" in description_lower: found_genres.append("Adventure")
        if "strategy" in description_lower: found_genres.append("Strategy")
        if "puzzle" in description_lower: found_genres.append("Puzzle")
        if "action" in description_lower: found_genres.append("Action")
        if "simulation" in description_lower: found_genres.append("Simulation")

        genre_str = ",".join(list(set(found_genres))) # Use set to avoid duplicate genres
        if genre_str:
            conn = sqlite3.connect(self.db.db_path)
            conn.execute("UPDATE games SET genre = ? WHERE title = ?", (genre_str, title))
            conn.commit()
            conn.close()
            print(f"Tagged '{title}' with genres: {genre_str}")
        return genre_str
