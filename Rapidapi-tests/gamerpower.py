import http.client
import json # Import the json module
import sys # Import sys for sys.exit

conn = http.client.HTTPSConnection("gamerpower.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "gamerpower.p.rapidapi.com", }

conn.request( "GET", "/api/filter?platform=epic-games-store.steam.android&type=game.loot", headers=headers, )

res = conn.getresponse()
data = res.read()

# Decode the data, parse it as JSON, and save to a file
try:
    json_data = json.loads(data.decode("utf-8"))
    with open("gamerpower_output.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)
    print("Output saved to gamerpower_output.json")
except json.JSONDecodeError:
    print("Failed to decode JSON response.")
    print("Raw response:", data.decode("utf-8", errors="replace"))
    sys.exit(1) # Exit with a non-zero status to indicate failure
