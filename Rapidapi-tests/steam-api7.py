import http.client

conn = http.client.HTTPSConnection("steam-api7.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "steam-api7.p.rapidapi.com", }

conn.request( "GET", "/appDetails/requirements/271590?plainText=true&platform=all&type=all&lang=english", headers=headers, )

res = conn.getresponse() data = res.read()

print(data.decode("utf-8"))
