import http.client

conn = http.client.HTTPSConnection("50000-games-collection.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "50000-games-collection.p.rapidapi.com", }

conn.request( "GET", "/rapidapi/video_game_reviews/get_game.php?page_no=1&genre=Adventure&age_group=Teens&platform=PC&publisher=Epic%20Games&developer=Game%20Freak&release_year=2015&multiplayer=Yes&game_mode=Online", headers=headers, )

res = conn.getresponse() data = res.read()

print(data.decode("utf-8"))
