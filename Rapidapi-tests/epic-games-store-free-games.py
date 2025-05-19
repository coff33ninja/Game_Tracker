import http.client
import json 
import sys # Import sys for sys.exit

conn = http.client.HTTPSConnection("epic-games-store-free-games.p.rapidapi.com")

headers = {
    "x-rapidapi-key": "47390d682cmsh4cd19bd83e78d56p1341d9jsn4f3d7d58a6b6",
    "x-rapidapi-host": "epic-games-store-free-games.p.rapidapi.com",
}

conn.request("GET", "/free?country=US", headers=headers)

res = conn.getresponse()
data = res.read()

# Get the JSON data and save to a file
try:
    json_data = json.loads(data.decode("utf-8"))
    with open("epic_games_store_free_games_output.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)
    print("Output saved to epic_games_store_free_games_output.json")
except json.JSONDecodeError:
    print("Failed to decode JSON response.")
    print("Raw response:", data.decode("utf-8", errors="replace"))
    sys.exit(1) # Exit with a non-zero status to indicate failure
