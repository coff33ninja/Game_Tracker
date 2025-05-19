import http.client
import json # Import the json module

conn = http.client.HTTPSConnection("steam-api7.p.rapidapi.com")

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "steam-api7.p.rapidapi.com", }

conn.request( "GET", "/appDetails/requirements/271590?plainText=true&platform=all&type=all&lang=english", headers=headers, )

res = conn.getresponse()
data = res.read()

# Decode the data, parse it as JSON, and save to a file
try:
    json_data = json.loads(data.decode("utf-8"))
    with open("steam_api7_output.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)
    print("Output saved to steam_api7_output.json")
except json.JSONDecodeError:
    print("Failed to decode JSON response.")
    print("Raw response:", data.decode("utf-8"))
