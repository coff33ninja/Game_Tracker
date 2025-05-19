lets use rapidapi instead

import http.client

conn = http.client.HTTPSConnection("free-to-play-games-database.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "free-to-play-games-database.p.rapidapi.com", }

conn.request("GET", "/api/games", headers=headers)

res = conn.getresponse() data = res.read()

print(data.decode("utf-8"))

import http.client

conn = http.client.HTTPSConnection("epic-games-store-free-games.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "epic-games-store-free-games.p.rapidapi.com", }

conn.request("GET", "/free?country=US", headers=headers)

res = conn.getresponse() data = res.read()

print(data.decode("utf-8"))

import http.client

conn = http.client.HTTPSConnection("gamerpower.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "gamerpower.p.rapidapi.com", }

conn.request( "GET", "/api/filter?platform=epic-games-store.steam.android&type=game.loot", headers=headers, )

res = conn.getresponse() data = res.read()

print(data.decode("utf-8"))

import requests

url = "https://free-epic-games.p.rapidapi.com/free"

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "free-epic-games.p.rapidapi.com", }

response = requests.get(url, headers=headers)

print(response.json())

import http.client

conn = http.client.HTTPSConnection("steam-game-search-and-details.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "steam-game-search-and-details.p.rapidapi.com", }

conn.request( "GET", "/game_details/search_like/game_id/?search_value=1547890%20", headers=headers )

res = conn.getresponse() data = res.read()

print(data.decode("utf-8"))

import http.client

conn = http.client.HTTPSConnection("steam-api7.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "steam-api7.p.rapidapi.com", }

conn.request( "GET", "/appDetails/requirements/271590?plainText=true&platform=all&type=all&lang=english", headers=headers, )

res = conn.getresponse() data = res.read()

print(data.decode("utf-8"))

import http.client

conn = http.client.HTTPSConnection("50000-games-collection.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "50000-games-collection.p.rapidapi.com", }

conn.request( "GET", "/rapidapi/video_game_reviews/get_game.php?page_no=1&genre=Adventure&age_group=Teens&platform=PC&publisher=Epic%20Games&developer=Game%20Freak&release_year=2015&multiplayer=Yes&game_mode=Online", headers=headers, )

res = conn.getresponse() data = res.read()

print(data.decode("utf-8"))

import http.client

conn = http.client.HTTPSConnection("video-game-news.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "video-game-news.p.rapidapi.com", }

conn.request("GET", "/all", headers=headers)

res = conn.getresponse() data = res.read()

print(data.decode("utf-8")) import http.client

conn = http.client.HTTPSConnection("video-game-price.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "video-game-price.p.rapidapi.com", }

conn.request( "GET", "/game?full_name=Super%20Mario%20Bros&name_contains=Mario&console_name=NES&region=NTSC", headers=headers, )

res = conn.getresponse() data = res.read()

print(data.decode("utf-8"))

import http.client

conn = http.client.HTTPSConnection("epic-store-games.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "epic-store-games.p.rapidapi.com", }

conn.request( "GET", "/comingSoon?searchWords=Assasin&categories=All&locale=us&country=us", headers=headers, )

res = conn.getresponse() data = res.read()

print(data.decode("utf-8")) import http.client

conn = http.client.HTTPSConnection("all-games-search-db.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "all-games-search-db.p.rapidapi.com", }

conn.request( "GET", "/search/suggest?l=english&use_store_query=1&use_search_spellcheck=1&search_creators_and_tags=1&realm=1&term=gta&cc=IN&excluded_content_descriptors=%5B%0A%20%203%2C%0A%20%204%0A%5D&f=games&v=28442543", headers=headers, )

res = conn.getresponse() data = res.read()

print(data.decode("utf-8"))
