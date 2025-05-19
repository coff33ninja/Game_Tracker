# price_tracker.py
import aiohttp
from bs4 import BeautifulSoup
from db_manager import DBManager


class PriceTracker:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager

    async def get_game_price(self, title, platform):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://isthereanydeal.com/search/?q={title}"
            ) as resp:
                soup = BeautifulSoup(await resp.text(), "html.parser")
                price_elem = soup.select_one(".price")
                price = float(price_elem.text.replace("$", "")) if price_elem else None
                if price:
                    conn = sqlite3.connect(self.db.db_path)
                    conn.execute(
                        "UPDATE games SET price = ? WHERE title = ? AND platform = ?",
                        (price, title, platform),
                    )
                    conn.commit()
                    conn.close()
                return price
