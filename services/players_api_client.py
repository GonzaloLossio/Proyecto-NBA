from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog

def fetch_players(search = None):
    all_players = players.get_players()
    if search:
        return [p for p in all_players if search.lower() in p["full_name"].lower()]
    return players

def fetch_players_stats(player_id,season):
    gamelog = playergamelog.PlayerGameLog(player_id=player_id,season=season)
    data = gamelog.get_normalized_dict()
    return data["PlayerGameLog"]