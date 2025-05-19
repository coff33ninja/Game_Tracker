# multi_language.py
from ai_module import AIModule
from db_manager import DBManager
import aiohttp
from bs4 import BeautifulSoup # For HTML parsing


class MultiLanguage:
    def __init__(self, ai_module: AIModule, db_manager: DBManager):
        self.ai = ai_module
        self.db = db_manager

    async def scrape_non_english(self, url, platform, locale="de"):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"Accept-Language": locale}) as resp:
                if resp.status != 200:
                    print(f"Failed to fetch non-English page {url}, status: {resp.status}")
                    return

                html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")

                # --- Placeholder for actual HTML parsing logic ---
                # This part is highly dependent on the structure of the target non-English page.
                # You'll need to inspect the page (e.g., Epic Games German free games page)
                # and write selectors to extract game titles and their specific URLs.
                # For demonstration, let's assume we find game titles in <h3> tags
                # and their links in the parent <a> tag. This is a very generic example.

                # Example: (This will likely NOT work as is and needs specific selectors)
                game_elements = soup.select(".some-game-container-class") # Replace with actual selector
                for element in game_elements:
                    title_tag = element.select_one(".game-title-class") # Replace
                    link_tag = element.select_one("a.game-link-class")   # Replace

                    if title_tag and link_tag and link_tag.has_attr('href'):
                        original_title = title_tag.text.strip()
                        game_url = link_tag['href']
                        if not game_url.startswith("http"): # Make URL absolute if relative
                            base_url = "/".join(url.split("/")[:3]) # e.g., https://store.epicgames.com
                            game_url = base_url + game_url

                        print(f"Found non-English game: {original_title} at {game_url} ({locale})")
                        # Note: Translation is a complex task. For now, we store the original title.
                        # A dedicated translation model/API would be needed for actual translation.
                        self.db.add_game(
                            title=original_title, # Storing original title
                            platform=platform,
                            url=game_url,
                            end_date=None, # End date might also need specific scraping
                            status="active",
                            language=locale,
                        )
                    else:
                        print(f"Could not extract title/url from an element on {url}")
                # --- End of placeholder ---

                # The old AI-based extraction and translation is removed as it's not
                # what the current AIModule is designed for.
                # result = self.ai.parse_text(html) # This would only classify the whole page
                # if result and result["title"] and result["url"]:
                #     translated_title = self.ai.parse_text(
                #         f"Translate: {result['title']} to English"
                #     )["translated_text"] # This was incorrect
                #     self.db.add_game(...)
