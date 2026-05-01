from flask import Blueprint,request,jsonify
from services.players_api_client import fetch_players,fetch_players_stats,fetch_player_trends,fetch_compare_players
from extensions import cache

players_bp = Blueprint("players",__name__)

@players_bp.route("/search")
def search_player():
    name = request.args.get("name")

    if not name or len (name)<3:
        return jsonify({"Error : Ingrese al menos 3 letras para poder buscar un jugador"}), 400
    
    raw_data = fetch_players(name)

    if not raw_data:
        return jsonify({"RESULTADOS" : [] , "Mensaje" : "Jugador No encotrado"})
    
    clean_data = []
    clean_data = [{
        "id" : p["id"],
        "full_name" : p["full_name"],
        "is_active" : p["is_active"],
    }for p in raw_data]

    return jsonify({"Resultados" : clean_data})

@players_bp.route("/stats")
@cache.cached(timeout=300, query_string=True)
def player_stat():
    player_id = request.args.get("id")
    season = request.args.get("season","2023-24")

    if not player_id:
        return jsonify({"Error" : "Se requiere el ID del jugador"})
    
    raw_data = fetch_players_stats(player_id = player_id, season =season)

    clean_data = [{
        "date": stat["GAME_DATE"],
        "points": stat["PTS"],
        "assists" : stat["AST"],
        "rebounds" : stat["REB"]
    } for stat in raw_data]

    min_points = request.args.get("min_points")

    if min_points:
        clean_data = [g for g in clean_data if g["points"] >= int(min_points)]


    return jsonify(clean_data)

@players_bp.route("/trends")
@cache.cached(timeout=300, query_string=True)
def player_trends():
    player_id = request.args.get("id")
    season = request.args.get("season","2023-24")

    if not player_id:
        return jsonify({"Error: Se requiere el ID del jugador"})
    
    data = fetch_player_trends(player_id=player_id,season=season)

    if not data:
        return jsonify({"Error: no se encontraron los datos para este jugador"})
    
    return data

@players_bp.route("/compare")
@cache.cached(timeout=300, query_string=True)
def compare_players():
    first_id = request.args.get("id1")
    second_id = request.args.get("id2")
    season = request.args.get("season","2023-24")

    if not first_id or not second_id:
        return jsonify({"Error : Se requiere los 2 IDS de los jugadores"})
    
    data = fetch_compare_players(first_id=first_id,second_id=second_id,season=season)

    if not data:
        return jsonify({"Error : no se encontraron los datos de los jugadores"})
    
    return data