import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright


async def scrape_epic_games():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US"
        ) as resp:
            data = await resp.json()
            samples = []
            for game in data["data"]["Catalog"]["searchStore"]["elements"]:
                slug = None
                if "slug" in game and game["slug"]:
                    slug = game["slug"]
                elif "productSlug" in game and game["productSlug"]:
                    slug = game["productSlug"]
                elif "catalogNs" in game and game["catalogNs"].get("mappings"):
                    slug = game["catalogNs"]["mappings"][0].get("pageSlug")

                if not slug:
                    print(f"Skipping game with no slug: {game.get('title', 'Unknown')}")
                    continue

                if game["price"]["totalPrice"]["discountPrice"] == 0:
                    text = f"Free on Epic: {game['title']} https://store.epicgames.com/en-US/p/{slug}"
                    end_date = ""
                    if game.get("promotions") and game["promotions"].get(
                        "promotionalOffers"
                    ):
                        try:
                            end_date = (
                                game["promotions"]["promotionalOffers"][0]
                                .get("endDate", "")
                                .replace("Z", "+00:00")
                            )
                        except (IndexError, TypeError):
                            print(
                                f"No valid promotionalOffers for: {game.get('title', 'Unknown')}"
                            )
                    samples.append(
                        {
                            "text": text,
                            "labels": {
                                "is_free": 1,
                                "title": game["title"],
                                "url": f"https://store.epicgames.com/en-US/p/{slug}",
                                "end_date": (
                                    datetime.fromisoformat(end_date).strftime(
                                        "%Y-%m-%d"
                                    )
                                    if end_date
                                    else ""
                                ),
                            },
                        }
                    )
                else:
                    text = f"{game['title']} for ${game['price']['totalPrice']['originalPrice']/100:.2f}"
                    samples.append(
                        {
                            "text": text,
                            "labels": {
                                "is_free": 0,
                                "title": game["title"],
                                "url": "",
                                "end_date": "",
                            },
                        }
                    )
            print(f"scrape_epic_games: {len(samples)} samples")
            return samples


async def scrape_amazon_prime():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://gaming.amazon.com/home") as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            samples = []
            for div in soup.select("div[data-a-target='offer-card']"):
                if "Free with Prime" in div.text:
                    title = (
                        div.find("h3").text.strip()
                        if div.find("h3")
                        else "Unknown Game"
                    )
                    url = div.find("a")["href"] if div.find("a") else ""
                    text = f"Free with Prime: {title} {url}"
                    samples.append(
                        {
                            "text": text,
                            "labels": {
                                "is_free": 1,
                                "title": title,
                                "url": url,
                                "end_date": "",
                            },
                        }
                    )
            for div in soup.select("div.game-card:not([data-a-target='offer-card'])")[
                :5
            ]:
                title = (
                    div.find("h3").text.strip() if div.find("h3") else "Unknown Game"
                )
                text = f"Game: {title} (Not Free)"
                samples.append(
                    {
                        "text": text,
                        "labels": {
                            "is_free": 0,
                            "title": title,
                            "url": "",
                            "end_date": "",
                        },
                    }
                )
            print(f"scrape_amazon_prime: {len(samples)} samples")
            return samples


async def scrape_gog():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.gog.com/en/games?priceRange=0,0") as resp:
            soup = BeautifulSoup(await resp.text(), "html.parser")
            samples = []
            for div in soup.select("div.product-tile"):
                if "Free" in div.text:
                    title = (
                        div.find("span", class_="product-title").text.strip()
                        if div.find("span", class_="product-title")
                        else "Unknown Game"
                    )
                    url = div.find("a")["href"] if div.find("a") else ""
                    text = f"Free on GOG: {title} {url}"
                    samples.append(
                        {
                            "text": text,
                            "labels": {
                                "is_free": 1,
                                "title": title,
                                "url": url,
                                "end_date": "",
                            },
                        }
                    )
            print(f"scrape_gog: {len(samples)} samples")
            return samples


async def scrape_steam_non_free():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://store.steampowered.com/search/?sort_by=Released_DESC"
        ) as resp:
            soup = BeautifulSoup(await resp.text(), "html.parser")
            samples = []
            for div in soup.select("div.search_result_row")[:10]:
                title = (
                    div.find("span", class_="title").text.strip()
                    if div.find("span", class_="title")
                    else "Unknown Game"
                )
                price = div.find("div.discount_original_price")
                if price and "Free" not in price.text:
                    text = f"{title} for {price.text}"
                    samples.append(
                        {
                            "text": text,
                            "labels": {
                                "is_free": 0,
                                "title": title,
                                "url": "",
                                "end_date": "",
                            },
                        }
                    )
            print(f"scrape_steam_non_free: {len(samples)} samples")
            return samples


async def scrape_ubisoft():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto("https://store.ubi.com/us/free-games", timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=30000)
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            samples = []
            for div in soup.select("div.product-tile"):
                if "Free" in div.text.lower():
                    title = (
                        div.find("h3").text.strip()
                        if div.find("h3")
                        else "Unknown Game"
                    )
                    url = div.find("a")["href"] if div.find("a") else ""
                    if not url.startswith("http"):
                        url = f"https://store.ubi.com{url}"
                    text = f"Free on Ubisoft: {title} {url}"
                    samples.append(
                        {
                            "text": text,
                            "labels": {
                                "is_free": 1,
                                "title": title,
                                "url": url,
                                "end_date": "",
                            },
                        }
                    )
                else:
                    title = (
                        div.find("h3").text.strip()
                        if div.find("h3")
                        else "Unknown Game"
                    )
                    price = div.find("span", class_="price") or div.find(
                        "span", class_="amount"
                    )
                    if price and "Free" not in price.text:
                        text = f"{title} for {price.text.strip()}"
                        samples.append(
                            {
                                "text": text,
                                "labels": {
                                    "is_free": 0,
                                    "title": title,
                                    "url": "",
                                    "end_date": "",
                                },
                            }
                        )
            print(f"scrape_ubisoft: {len(samples)} samples")
            return samples
        except Exception as e:
            print(f"Error in scrape_ubisoft: {e}")
            return []
        finally:
            await browser.close()


async def scrape_itch_io():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://itch.io/games/free") as resp:
                soup = BeautifulSoup(await resp.text(), "html.parser")
                samples = []
                for div in soup.select("div.game_cell"):
                    price = div.find("span", class_="price_value")
                    if price and price.text.lower() in ["free", "$0.00"]:
                        title = (
                            div.find("a", class_="title").text.strip()
                            if div.find("a", class_="title")
                            else "Unknown Game"
                        )
                        url = (
                            div.find("a", class_="title")["href"]
                            if div.find("a", class_="title")
                            else ""
                        )
                        text = f"Free on Itch.io: {title} {url}"
                        samples.append(
                            {
                                "text": text,
                                "labels": {
                                    "is_free": 1,
                                    "title": title,
                                    "url": url,
                                    "end_date": "",
                                },
                            }
                        )
                print(f"scrape_itch_io: {len(samples)} samples")
                return samples
        except Exception as e:
            print(f"Error in scrape_itch_io: {e}")
            return []


async def scrape_indiegala():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://www.indiegala.com/freebies") as resp:
                soup = BeautifulSoup(await resp.text(), "html.parser")
                samples = []
                for div in soup.select("div.product-box"):
                    if "Free" in div.text.lower():
                        title = (
                            div.find("h3", class_="product-title").text.strip()
                            if div.find("h3", class_="product-title")
                            else "Unknown Game"
                        )
                        url = div.find("a")["href"] if div.find("a") else ""
                        text = f"Free on IndieGala: {title} {url}"
                        samples.append(
                            {
                                "text": text,
                                "labels": {
                                    "is_free": 1,
                                    "title": title,
                                    "url": url,
                                    "end_date": "",
                                },
                            }
                        )
                print(f"scrape_indiegala: {len(samples)} samples")
                return samples
        except Exception as e:
            print(f"Error in scrape_indiegala: {e}")
            return []


async def scrape_humble_bundle():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                "https://www.humblebundle.com/store/free-games"
            ) as resp:
                soup = BeautifulSoup(await resp.text(), "html.parser")
                samples = []
                for div in soup.select("div.product-card"):
                    if "Free" in div.text.lower():
                        title = (
                            div.find("h3").text.strip()
                            if div.find("h3")
                            else "Unknown Game"
                        )
                        url = div.find("a")["href"] if div.find("a") else ""
                        text = f"Free on Humble: {title} {url}"
                        samples.append(
                            {
                                "text": text,
                                "labels": {
                                    "is_free": 1,
                                    "title": title,
                                    "url": url,
                                    "end_date": "",
                                },
                            }
                        )
                print(f"scrape_humble_bundle: {len(samples)} samples")
                return samples
        except Exception as e:
            print(f"Error in scrape_humble_bundle: {e}")
            return []


async def scrape_microsoft_store():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.microsoft.com/en-us/store/b/free-games")
        await page.wait_for_load_state("networkidle")
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")
        samples = []
        for div in soup.select("div.card"):
            if "Free" in div.text.lower():
                title = (
                    div.find("h3").text.strip() if div.find("h3") else "Unknown Game"
                )
                url = div.find("a")["href"] if div.find("a") else ""
                text = f"Free on Microsoft: {title} {url}"
                samples.append(
                    {
                        "text": text,
                        "labels": {
                            "is_free": 1,
                            "title": title,
                            "url": url,
                            "end_date": "",
                        },
                    }
                )
        await browser.close()
        print(f"scrape_microsoft_store: {len(samples)} samples")
        return samples


async def scrape_x_posts():
    posts = [
        "Free on Epic: Dead Island 2 https://store.epicgames.com/en-US/p/dead-island-2 #freegame",
        "GOG giveaway: Witcher 3 https://www.gog.com/game/witcher-3",
        "New release: Starfield $69.99 #gaming",
    ]
    samples = []
    for post in posts:
        is_free = 1 if "free" in post.lower() or "giveaway" in post.lower() else 0
        title_match = re.search(r"[\w\s:]+(?= https?://|$)", post)
        title = title_match.group().strip() if title_match else "Unknown"
        platform_prefixes = ["Free on Epic: ", "GOG giveaway: "]
        for prefix in platform_prefixes:
            if title.startswith(prefix):
                title = title[len(prefix) :].strip()
                break
        url_match = re.search(r"https?://[^\s]+", post)
        url = url_match.group() if url_match else ""
        samples.append(
            {
                "text": post,
                "labels": {
                    "is_free": is_free,
                    "title": title,
                    "url": url,
                    "end_date": "",
                },
            }
        )
    print(f"scrape_x_posts: {len(samples)} samples")
    return samples


async def generate_dataset(output_file="dataset.jsonl"):
    samples = []
    scrapers = [
        scrape_epic_games,
        scrape_amazon_prime,
        scrape_gog,
        scrape_steam_non_free,
        scrape_ubisoft,
        scrape_itch_io,
        scrape_indiegala,
        scrape_humble_bundle,
        scrape_x_posts,
    ]

    for scraper in scrapers:
        try:
            scraper_samples = await scraper()
            samples.extend(scraper_samples)
        except Exception as e:
            print(f"Error in {scraper.__name__}: {e}")

    manual_samples = [
        {
            "text": '<div class="offer-title">Free with Prime: Star Wars: Knights of the Old Republic</div><a href="https://gaming.amazon.com/kotor">Claim</a>',
            "labels": {
                "is_free": 1,
                "title": "Star Wars: Knights of the Old Republic",
                "url": "https://gaming.amazon.com/kotor",
                "end_date": "",
            },
        },
        {
            "text": '<div class="game-price">Cyberpunk 2077: $59.99</div>',
            "labels": {
                "is_free": 0,
                "title": "Cyberpunk 2077",
                "url": "",
                "end_date": "",
            },
        },
        {
            "text": "Free on GOG: Witcher 3 https://www.gog.com/game/witcher-3 until 2025-06-01",
            "labels": {
                "is_free": 1,
                "title": "Witcher 3",
                "url": "https://www.gog.com/game/witcher-3",
                "end_date": "2025-06-01",
            },
        },
    ]
    samples.extend(manual_samples)

    with open(output_file, "w", encoding="utf-8") as f:
        for sample in samples:
            f.write(json.dumps(sample) + "\n")

    print(f"Generated {len(samples)} samples in {output_file}")


if __name__ == "__main__":
    asyncio.run(generate_dataset())
