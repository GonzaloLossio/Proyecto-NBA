from flask import Blueprint,request,jsonify
from services.players_api_client import fetch_players, fetch_players_stats

players_bp = Blueprint("players",__name__)

@players_bp.route('/search')
def search_player():
    name  = request.args.get("name")

    if not name or len(name)<3:
        return jsonify({"Error: Ingrese al menos 3 letras para poder buscar un jugador"})
    
    raw_data = fetch_players(search = name)

    if not raw_data.get("data"):
        return jsonify({"Resultados" : [], "Mensaje": "Error, no se encontro el jugador"})
    
    clean_data = []
    for player in raw_data.get("data",[]):
        clean_data.append({
            "id": player["id"], "full_name" : f"{player['first_name']} {player['last_name']}", "team" : player["team"]["abbreviation"], 
            "position" : player["position"]
        })
    return jsonify({"Resultados": clean_data})    


@players_bp.route('/stats')
def player_stats():
    player_id = request.args.get("id")
    season = request.args.get("season", 2023)

    if not player_id:
        return jsonify({"error": "Se requiere el ID del jugador"}), 400

    raw_data = fetch_players_stats(id=player_id, season=season)

    clean_data = []
    
    for stat in raw_data.get("data", []):
        clean_data.append({
            "date": stat["game"]["date"], 
            "points": stat["pts"], 
            "assists": stat["ast"], 
            "rebounds": stat["reb"]
        })

    clean_data.sort(key=lambda x: x["date"])
    return jsonify(clean_data)