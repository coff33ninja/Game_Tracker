import requests

url = "https://free-epic-games.p.rapidapi.com/free"

headers = {
    "x-rapidapi-key": "24cf6fe557msha7843d66020cd4fp14f0c0jsnb142b98926a9",
    "x-rapidapi-host": "free-epic-games.p.rapidapi.com",
}

response = requests.get(url, headers=headers)

print(response.json())
