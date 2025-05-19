# genre_tagging.py
from ai_module import AIModule
from db_manager import DBManager
import sqlite3 # Import for database operations


class GenreTagging:
    def __init__(self, ai_module: AIModule, db_manager: DBManager):
        self.ai = ai_module
        self.db = db_manager

    def tag_game(self, title, description):
        # The AIModule's parse_text method no longer extracts genres.
        # It's now focused on "is_free" classification and providing embeddings.
        # Genre tagging would require a different approach:
        # 1. A dedicated multi-label classification model trained on game descriptions and genres.
        # 2. Keyword extraction from the description.
        # 3. Using an external API that provides genre information.
        # For now, this function will be a placeholder and not update genres via AI.
        # Genres might be populated by scrapers if they can find that info, or manually.

        print(f"GenreTagging.tag_game called for '{title}'. AI-based genre extraction is currently not implemented with this AIModule.")
        # Example: If you had a keyword-based approach:
        # found_genres = []
        # if "rpg" in description.lower(): found_genres.append("RPG")
        # if "shooter" in description.lower(): found_genres.append("Shooter")
        # genre_str = ",".join(found_genres)
        # if genre_str:
        #     conn = sqlite3.connect(self.db.db_path)
        #     conn.execute("UPDATE games SET genre = ? WHERE title = ?", (genre_str, title))
        #     conn.commit()
        #     conn.close()
        # return genre_str
        return "" # Return empty string or None as genres are not being tagged by this method now.
