from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from utils.stats_helper import calcAverages

def fetch_players(search = None):
    all_players = players.get_players()
    if search:
        return [p for p in all_players if search.lower() in p["full_name"].lower()]
    return all_players

def fetch_players_stats(player_id,season):
    gamelog = playergamelog.PlayerGameLog(player_id=player_id,season=season)
    data = gamelog.get_normalized_dict()
    return data["PlayerGameLog"]

def fetch_player_trends(player_id,season):
    stats = fetch_players_stats(player_id=player_id,season=season)

    if not stats:
        return None
    
    last_5 = stats[:5]

    avg_last_5 = calcAverages(last_5)
    avg_season = calcAverages(stats)

    if avg_last_5["points"] > avg_season['points']:
        trend = "subiendo"
    elif avg_last_5["points"] < avg_season['points']:
        trend = "bajando"
    else:
        trend = "estable"

    hot_streak = avg_last_5["points"]>=25     

    info_player = players.find_player_by_id(int(player_id))
    full_name = info_player["full_name"]
    
    return{
        "player_id" : player_id,
        "season" : season,
        "name" : full_name,
        "last_5_games" :[{
            "date" : g["GAME_DATE"],
            "points" : g["PTS"],
            "assists" : g["AST"],
            "rebounds" : g["REB"]
        } for g in last_5],
        "averages_last_5" : avg_last_5,
        "season_averages" : avg_season,
        "hot_streak" :  hot_streak,
        "trend" : trend
    }

def fetch_compare_players(first_id,second_id,season):
    first_player_stats = fetch_player_trends(first_id,season)
    second_player_stats = fetch_player_trends(second_id,season)

    if not first_player_stats or not second_player_stats:
        return None
    
    winner = {
        "points" : first_player_stats["name"] if  first_player_stats["season_averages"]["points"] > second_player_stats["season_averages"]["points"] else second_player_stats["name"] ,
        "assists" : first_player_stats["name"]  if  first_player_stats["season_averages"]["assists"] > second_player_stats["season_averages"]["assists"] else second_player_stats["name"] ,
        "rebounds" : first_player_stats["name"]  if  first_player_stats["season_averages"]["rebounds"] > second_player_stats["season_averages"]["rebounds"] else second_player_stats["name"] 
    }

    return{
        "player_1" : first_player_stats,
        "player_2" : second_player_stats,
        "winner" : winner
    }