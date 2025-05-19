import http.client
import json # Import the json module

conn = http.client.HTTPSConnection("steam-game-search-and-details.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "steam-game-search-and-details.p.rapidapi.com", }

conn.request( "GET", "/game_details/search_like/game_id/?search_value=1547890%20", headers=headers )

res = conn.getresponse()
data = res.read()

# Decode the data, parse it as JSON, and save to a file
try:
    json_data = json.loads(data.decode("utf-8"))
    with open("steam_game_search_and_details_output.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)
    print("Output saved to steam_game_search_and_details_output.json")
except json.JSONDecodeError:
    print("Failed to decode JSON response.")
    print("Raw response:", data.decode("utf-8"))
