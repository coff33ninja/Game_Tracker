# wishlist.py
import aiohttp
from db_manager import DBManager
from notifications import Notifications


class Wishlist:
    def __init__(self, db_manager: DBManager, notifications: Notifications):
        self.db = db_manager
        self.notifications = notifications

    async def check_steam_wishlist(self, steam_id, api_key):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://store.steampowered.com/wishlist/profiles/{steam_id}/wishlistdata/"
            ) as resp:
                data = await resp.json()
                for appid, game in data.items():
                    if game.get("free"):
                        self.notifications.send_desktop_notification(
                            "Wishlist Free Game", f"{game['name']} is free on Steam!"
                        )
