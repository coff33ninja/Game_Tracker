# playtime.py
import aiohttp
from db_manager import DBManager


class Playtime:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager

    async def get_steam_playtime(self, steam_id, api_key):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/?key={api_key}&steamid={steam_id}"
            ) as resp:
                data = await resp.json()
                for game in data["response"].get("games", []):
                    conn = sqlite3.connect(self.db.db_path)
                    conn.execute(
                        "UPDATE games SET playtime = ? WHERE title = ? AND platform = 'Steam'",
                        (game["playtime_forever"] / 60, game["name"]),
                    )
                    conn.commit()
                    conn.close()
