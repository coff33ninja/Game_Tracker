import http.client

conn = http.client.HTTPSConnection("steam-game-search-and-details.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "steam-game-search-and-details.p.rapidapi.com", }

conn.request( "GET", "/game_details/search_like/game_id/?search_value=1547890%20", headers=headers )

res = conn.getresponse() data = res.read()

print(data.decode("utf-8"))
