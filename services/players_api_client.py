import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
BASE_URL = os.getenv('BASE_URL')
HEADERS = {"Authorization" : API_KEY }

def fetch_players(search = None):
    params = {}
    if search:
        params ["search"] = search
    response = requests.get(f"{BASE_URL}/nba/v1/players",headers=HEADERS, params=params)


          
    return response.json()

def fetch_players_stats(id,season):
    params = {
        "player_ids[]": id,
        "seasons[]": season,
        "per_page[]" : 100
    }
    response = requests.get(f"{BASE_URL}/nba/v1/stats", headers=HEADERS, params=params)
    return response.json()

