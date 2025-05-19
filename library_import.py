# library_import.py
import aiohttp
from db_manager import DBManager


class LibraryImport:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager

    async def import_steam_library(self, steam_id, api_key):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={api_key}&steamid={steam_id}&include_appinfo=1"
            ) as resp:
                data = await resp.json()
                for game in data["response"].get("games", []):
                    self.db.add_game(
                        title=game["name"],
                        platform="Steam",
                        url=f"https://store.steampowered.com/app/{game['appid']}",
                        status="owned",
                        acquisition_date=None,
                    )

    async def import_epic_library(self, user_id, auth_token):
        # Note: Epic's API requires OAuth, which may need user login. Placeholder for GraphQL query.
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://graphql.epicgames.com/graphql",
                headers={"Authorization": f"Bearer {auth_token}"},
            ) as resp:
                data = await resp.json()
                # Parse Epic library (implement based on API docs)
                for game in data.get("owned_games", []):
                    self.db.add_game(
                        title=game["title"],
                        platform="Epic",
                        url=game.get("url", ""),
                        status="owned",
                        acquisition_date=None,
                    )
