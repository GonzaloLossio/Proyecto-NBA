from flask import Blueprint,request,jsonify
from services.players_api_client import fetch_players, fetch_players_stats

players_bp = Blueprint("players",__name__)

@players_bp.route('/search')
def search_player():
    name  = request.args.get("name")

    if not name or len(name)<3:
        return jsonify({"Error: Ingrese al menos 3 letras para poder buscar un jugador"}) , 400
    
    raw_data = fetch_players(search = name)

    if not raw_data:
        return jsonify({"Resultados" : [], "Mensaje": "Error, no se encontro el jugador"})
    
    clean_data = []
    clean_data = [{
        "id": p["id"],
        "full_name": p["full_name"],
        "is_active": p["is_active"]
    }for p in raw_data]
    return jsonify({"Resultados": clean_data})    


@players_bp.route('/stats')
def player_stats():

    player_id = request.args.get("id")
    season = request.args.get("season", "2023-24")

    if not player_id:
        return jsonify({"error": "Se requiere el ID del jugador"}), 400

    raw_data = fetch_players_stats(player_id=player_id, season=season)

    clean_data = [{
        "date": stat["GAME_DATE"],
        "points": stat["PTS"],
        "assists" : stat["AST"],
        "rebounds" : stat["REB"]
    } for stat in raw_data]

    return jsonify(clean_data)