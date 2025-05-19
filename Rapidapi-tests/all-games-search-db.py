import http.client
import json # Import the json module
import sys # Import sys for sys.exit

conn = http.client.HTTPSConnection("all-games-search-db.p.rapidapi.com")

headers = {
    "x-rapidapi-key": "47390d682cmsh4cd19bd83e78d56p1341d9jsn4f3d7d58a6b6",
    "x-rapidapi-host": "all-games-search-db.p.rapidapi.com",
}

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
    # Print raw response, replacing characters that can't be easily displayed
    raw_response_str = data.decode("utf-8", errors="replace")
    # Ensure the string is printable on the current console by encoding and decoding with replacement
    console_encoding = sys.stdout.encoding if sys.stdout.encoding else 'utf-8'
    printable_response = raw_response_str.encode(console_encoding, errors='replace').decode(console_encoding)
    print("Raw response:", printable_response)
    sys.exit(1) # Exit with a non-zero status to indicate failure
