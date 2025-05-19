import http.client
import json # Import the json module

conn = http.client.HTTPSConnection("all-games-search-db.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "all-games-search-db.p.rapidapi.com", }

conn.request( "GET", "/search/suggest?l=english&use_store_query=1&use_search_spellcheck=1&search_creators_and_tags=1&realm=1&term=gta&cc=IN&excluded_content_descriptors=%5B%0A%20%203%2C%0A%20%204%0A%5D&f=games&v=28442543", headers=headers, )

res = conn.getresponse()
data = res.read()

# Decode the data, parse it as JSON, and save to a file
try:
    json_data = json.loads(data.decode("utf-8"))
    with open("all_games_search_db_output.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)
    print("Output saved to all_games_search_db_output.json")
except json.JSONDecodeError:
    print("Failed to decode JSON response.")
    print("Raw response:", data.decode("utf-8"))
