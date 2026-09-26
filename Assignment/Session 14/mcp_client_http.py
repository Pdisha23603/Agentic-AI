import requests
import json

url = "http://127.0.0.1:8000/mcp"

payload = {
    "jsonrpc":"2.0",
    "id":2,
    "method":"tools/call",
    "params":{
        "name":"get_song_recommendation",
        "arguments":{}
    }
}

response = requests.post(url, json=payload)

print(json.dumps(response.json(), indent=4))