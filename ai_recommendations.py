# ai_recommendations.py
from ai_module import AIModule
from db_manager import DBManager
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class AIRecommendations:
    def __init__(self, ai_module: AIModule, db_manager: DBManager):
        self.ai = ai_module
        self.db = db_manager

    def get_game_embeddings(self, titles):
        embeddings = []
        for title in titles:
            # Use the new get_embedding method which directly returns the embedding
            embedding = self.ai.get_embedding(title)
            embeddings.append(embedding[0] if embedding is not None and embedding.ndim > 1 else np.zeros(self.ai.model.config.hidden_size)) # embedding is (1, hidden_size)
        return np.array(embeddings).reshape(-1, self.ai.model.config.hidden_size) # Ensure correct shape

    def recommend_games(self):
        owned_games = self.db.get_games_by_status("owned")
        active_games = self.db.get_games_by_status("active")
        if not owned_games or not active_games:
            return []

        owned_titles = [g[1] for g in owned_games]
        active_titles = [g[1] for g in active_games]
        owned_embeddings = self.get_game_embeddings(owned_titles)
        active_embeddings = self.get_game_embeddings(active_titles)

        similarities = cosine_similarity(active_embeddings, owned_embeddings)
        top_indices = similarities.mean(axis=1).argsort()[-3:][
            ::-1
        ]  # Top 3 recommendations
        return [active_games[i] for i in top_indices]
