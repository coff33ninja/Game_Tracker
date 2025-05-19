# community_sharing.py
import aiohttp
from db_manager import DBManager


class CommunitySharing:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager

    async def share_to_discord(self, webhook_url):
        games = self.db.get_games_by_status("active")
        message = "\n".join(f"{g[1]} on {g[0]}: {g[2]}" for g in games)
        async with aiohttp.ClientSession() as session:
            await session.post(webhook_url, json={"content": message})
