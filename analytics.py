# analytics.py
from db_manager import DBManager


class Analytics:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager

    def get_platform_chart(self):
        counts = self.db.get_status_counts()
        platforms = ["Epic", "Amazon Prime", "GOG", "Steam", "Ubisoft"]
        data = [
            len([g for g in self.db.get_games_by_status("owned") if g[0] == p])
            for p in platforms
        ]
        return {
            "type": "bar",
            "data": {
                "labels": platforms,
                "datasets": [
                    {
                        "label": "Games Owned",
                        "data": data,
                        "backgroundColor": [
                            "#00FFFF",
                            "#FF69B4",
                            "#FFD700",
                            "#00FF00",
                            "#FF4500",
                        ],
                    }
                ],
            },
            "options": {"scales": {"y": {"beginAtZero": True}}},
        }
