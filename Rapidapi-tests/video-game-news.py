import http.client
import json # Import the json module

conn = http.client.HTTPSConnection("video-game-news.p.rapidapi.com") # Corrected hostname

headers = { "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9", "x-rapidapi-host": "video-game-news.p.rapidapi.com", }

conn.request("GET", "/all", headers=headers)

res = conn.getresponse()
data = res.read()

# Decode the data, parse it as JSON, and save to a file
try:
    json_data = json.loads(data.decode("utf-8"))
    with open("video_game_news_output.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)
    print("Output saved to video_game_news_output.json")
except json.JSONDecodeError:
    print("Failed to decode JSON response.")
    print("Raw response:", data.decode("utf-8"))
