import http.client

conn = http.client.HTTPSConnection("epic-games-store-free-games.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "epic-games-store-free-games.p.rapidapi.com", }

conn.request("GET", "/free?country=US", headers=headers)

res = conn.getresponse() data = res.read()

print(data.decode("utf-8"))
