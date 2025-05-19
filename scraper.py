# scraper.py
import aiohttp
from bs4 import BeautifulSoup
from pydantic import BaseModel
from datetime import datetime
from playwright.async_api import async_playwright # For Ubisoft
from ai_module import AIModule


class FreeGame(BaseModel):
    title: str
    platform: str
    url: str
    end_date: datetime | None


class GameScraper:
    def __init__(self, ai_module: AIModule = None):
        self.ai = ai_module

    async def check_epic_games(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US"
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    games_list = []
                    for game_data in data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", []):
                        if game_data.get("price", {}).get("totalPrice", {}).get("discountPrice", -1) == 0:
                            title = game_data.get("title")

                            slug = None
                            if "slug" in game_data and game_data["slug"]:
                                slug = game_data["slug"]
                            elif "productSlug" in game_data and game_data["productSlug"]:
                                slug = game_data["productSlug"]
                            elif "catalogNs" in game_data and game_data["catalogNs"].get("mappings"):
                                mappings = game_data["catalogNs"]["mappings"]
                                if mappings and len(mappings) > 0:
                                    slug = mappings[0].get("pageSlug")

                            if not title or not slug:
                                print(f"Epic Games: Skipping game due to missing title or slug: {game_data.get('id', 'Unknown ID')}")
                                continue

                            url = f"https://store.epicgames.com/en-US/p/{slug}"

                            end_date_obj = None
                            try:
                                promotions = game_data.get("promotions")
                                if promotions:
                                    promo_offers_wrapper = promotions.get("promotionalOffers")
                                    if promo_offers_wrapper and len(promo_offers_wrapper) > 0:
                                        first_promo_group = promo_offers_wrapper[0]
                                        actual_offers = first_promo_group.get("promotionalOffers")
                                        if actual_offers and len(actual_offers) > 0:
                                            end_date_str = actual_offers[0].get("endDate")
                                            if end_date_str:
                                                end_date_obj = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
                            except (IndexError, TypeError, AttributeError, ValueError) as e:
                                print(f"Epic Games: Error parsing end_date for {title}: {e}")

                            games_list.append(FreeGame(title=title, platform="Epic", url=url, end_date=end_date_obj))
                    return games_list
            except Exception as e:
                print(f"Error scraping Epic Games: {e}")
                return []

    async def check_amazon_prime(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://gaming.amazon.com/home") as resp:
                    resp.raise_for_status() # Good practice to check for HTTP errors
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    games = [
                        FreeGame(title=div.find("h3").text.strip(), platform="Amazon Prime", url=div.find("a")["href"] if div.find("a") else "", end_date=None)
                        for div in soup.select("div[data-a-target='offer-card']")
                        if "Free with Prime" in div.text
                    ]
                    # The AI fallback for Amazon Prime is removed for now due to issues with the current AI module setup.
                    # If you have a working AI parser for HTML, it could be re-added.
                    return games
            except Exception as e:
                print(f"Error scraping Amazon Prime: {e}")
                return []


    async def check_gog_games(self):
        games_list = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://www.gog.com/en/games?priceRange=0,0&discounted=true") as resp: # Added discounted=true
                    resp.raise_for_status()
                    soup = BeautifulSoup(await resp.text(), "html.parser")
                    for div in soup.select("product-tile"): # GOG uses custom elements
                        # Check if it's actually free, GOG sometimes lists "free weekends" or demos here.
                        # Looking for a clear "Free" indicator or $0.00 price.
                        # This might need more specific selectors if GOG's layout changes.
                        is_free_text = div.select_one("span[price-value='0.00']") # More specific
                        if is_free_text or "free" in str(div.select_one(".product-state")).lower():
                            title_tag = div.select_one("product-tile-title > span[translate]")
                            title = title_tag.text.strip() if title_tag else None

                            url_tag = div.select_one("a.product-tile__content")
                            url = url_tag['href'] if url_tag and url_tag.has_attr('href') else None

                            if title and url:
                                games_list.append(FreeGame(title=title, platform="GOG", url=url, end_date=None))
        except Exception as e:
            print(f"Error scraping GOG: {e}")
        return games_list

    async def check_ubisoft_games(self):
        games_list = []
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto("https://store.ubi.com/us/free-events", timeout=60000) # Free events page
                await page.wait_for_load_state("networkidle", timeout=30000)
                content = await page.content()
                await browser.close()

                soup = BeautifulSoup(content, "html.parser")
                # Ubisoft selectors can be tricky and change often.
                # This is a guess based on common patterns.
                for item in soup.select(".product-slot__main-link, .game-product-card__link"): # Example selectors
                    title_tag = item.select_one(".game-title, .prod-title")
                    title = title_tag.text.strip() if title_tag else None

                    url = item.get("href", "")
                    if not url.startswith("http"):
                        url = f"https://store.ubi.com{url}"

                    # Check for "free" text explicitly, as this page might list trials
                    if title and url and ("free" in item.text.lower() or "play for free" in item.text.lower()):
                         # Ubisoft free games are often timed events, end_date might be hard to scrape reliably
                        games_list.append(FreeGame(title=title, platform="Ubisoft", url=url, end_date=None))
        except Exception as e:
            print(f"Error scraping Ubisoft: {e}")
        return games_list

    async def check_itch_io_games(self):
        games_list = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://itch.io/games/free") as resp:
                    resp.raise_for_status()
                    soup = BeautifulSoup(await resp.text(), "html.parser")
                    for div in soup.select("div.game_cell"):
                        price_tag = div.select_one(".price_value")
                        if price_tag and price_tag.text.strip().lower() in ["free", "$0.00", "download"]:
                            title_tag = div.select_one("a.title.game_link, .game_title a")
                            title = title_tag.text.strip() if title_tag else None

                            url_tag = div.select_one("a.title.game_link, .game_title a")
                            url = url_tag['href'] if url_tag and url_tag.has_attr('href') else None
                            if url and not url.startswith("http"):
                                url = f"https://itch.io{url}"

                            if title and url:
                                games_list.append(FreeGame(title=title, platform="Itch.io", url=url, end_date=None))
        except Exception as e:
            print(f"Error scraping Itch.io: {e}")
        return games_list

    async def check_indiegala_games(self):
        games_list = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://freebies.indiegala.com/") as resp: # More specific URL
                    resp.raise_for_status()
                    soup = BeautifulSoup(await resp.text(), "html.parser")
                    for div in soup.select("div.product-row-info"): # Selector from their freebies page
                        title_tag = div.select_one("h3.product-title-big a, .article-title-medium a")
                        title = title_tag.text.strip() if title_tag else None

                        url_tag = div.select_one("h3.product-title-big a, .article-title-medium a")
                        url = url_tag['href'] if url_tag and url_tag.has_attr('href') else None

                        # Check for "free" text or $0 price if available
                        if title and url and "free" in div.text.lower(): # Simple check
                            games_list.append(FreeGame(title=title, platform="IndieGala", url=url, end_date=None))
        except Exception as e:
            print(f"Error scraping IndieGala: {e}")
        return games_list

    async def check_humble_bundle_games(self):
        games_list = []
        # Humble Bundle free games are rare and often part of specific promotions.
        # A dedicated "free games" page might not always have items.
        # This is a placeholder and might need adjustment based on current Humble layout.
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://www.humblebundle.com/store/search?sort=discount&filter=price_free") as resp:
                    resp.raise_for_status()
                    soup = BeautifulSoup(await resp.text(), "html.parser")
                    for item in soup.select(".entity-details"): # Generic selector, needs verification
                        title_tag = item.select_one(".entity-title")
                        title = title_tag.text.strip() if title_tag else None

                        # URL might be on a parent element or a specific link
                        url_tag = item.find_parent("a")
                        url = url_tag['href'] if url_tag and url_tag.has_attr('href') else None
                        if url and not url.startswith("http"):
                            url = f"https://www.humblebundle.com{url}"

                        if title and url: # Assuming items on this page are indeed free
                            games_list.append(FreeGame(title=title, platform="Humble Bundle", url=url, end_date=None))
        except Exception as e:
            print(f"Error scraping Humble Bundle: {e}")
        return games_list

    async def scrape_all(self):
        all_games = []
        all_games.extend(await self.check_epic_games())
        all_games.extend(await self.check_amazon_prime())
        all_games.extend(await self.check_gog_games())
        all_games.extend(await self.check_ubisoft_games())
        all_games.extend(await self.check_itch_io_games())
        all_games.extend(await self.check_indiegala_games())
        all_games.extend(await self.check_humble_bundle_games())
        # Note: Steam free promotional games are harder to scrape directly from a single page.
        # They are often announced on news sites or specific product pages.
        # For now, Steam is omitted from this general storefront scrape.
        return all_games
