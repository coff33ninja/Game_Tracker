import http.client

conn = http.client.HTTPSConnection("epic-store-games.p.rapidapi.com")

headers = {
    "x-rapidapi-key": "47390d682cmsh4cd19bd83e78d56p1341d9jsn4f3d7d58a6b6",
    "x-rapidapi-host": "epic-store-games.p.rapidapi.com",
}

conn.request( "GET", "/comingSoon?searchWords=Assasin&categories=All&locale=us&country=us", headers=headers, )

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
