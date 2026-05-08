from flask import Blueprint,request,jsonify
from services.games_api_client import fetch_scoreboard, fetch_standings,fetch_box_score
from utils.stats_helper import get_top_stat
from extensions import cache,limiter
from datetime import datetime
games_bp = Blueprint("games",__name__)


@games_bp.route("/scoreboard")
@limiter.limit("30 per minute")
@cache.cached(timeout=60, query_string=True)
def scoreboard():

    """
    Obtiene el marcador de los juegos de la NBA para una fecha específica.
    ---
    parametros:
      - name: game_date
        in: query
        type: string
        required: true
        description: Fecha en formato YYYY-MM-DD. Ej. 2024-05-15
      - name: team
        in: query
        type: string
        required: false
        description: Tricode del equipo para filtrar (NBA Tricode). Ej. LAL, GSW
    respuestas:
      200:
        description: Lista de juegos encontrados con sus respectivos estados y líderes.
      400:
        description: Fecha no proporcionada o formato inválido.
      502:
        description: Error al conectar con el servidor de la NBA.
    """

    game_date = request.args.get("game_date")
    team = request.args.get("team")

    if not game_date:
        return jsonify({"Error" : "Se requiere el parametro 'game_date' (YYYY-MM-DD)"}),400
    
    try:
        datetime.strptime(game_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"Error" : "Formato de fecha invalido. Use YYYY-MM-DD"}),400
    
    game = fetch_scoreboard(game_date=game_date)

    if game is None: 
        return jsonify({"Error" : "Error, no se pudo obtener informacion de la NBA"}),502
    
    if not game:
        return jsonify({"Error" : "No hay partidos programados para la fecha indicada", "Resultados" : []}),200
    
    clean_data = []

    for g in game:  
        clean_game = {
            "game_id" : g["gameId"],
            "status" : g["gameStatusText"],

            "home_team" : {
                "name": g["homeTeam"]["teamName"],
                "tricode": g["homeTeam"]["teamTricode"],
                "score": g["homeTeam"]["score"],
            },

            "away_team" : {
                "name" : g["awayTeam"]["teamName"],
                "tricode" : g["awayTeam"]["teamTricode"],
                "score" : g["awayTeam"]["score"],
            },

            "home_leaders" : None,
            "away_leaders" : None,
            
        }

        if g["gameStatus"] >=2:
            clean_game["home_leaders"] = {
                "name" : g["gameLeaders"]["homeLeaders"]["name"],
                "points" : g["gameLeaders"]["homeLeaders"]["points"],
                "assists" : g["gameLeaders"]["homeLeaders"]["assists"],
                "rebounds" : g["gameLeaders"]["homeLeaders"]["rebounds"],
            }
            clean_game["away_leaders"] = {
                "name" : g["gameLeaders"]["awayLeaders"]["name"],
                "points": g["gameLeaders"]["awayLeaders"]["points"],
                "assists": g["gameLeaders"]["awayLeaders"]["assists"],
                "rebounds": g["gameLeaders"]["awayLeaders"]["rebounds"],
            }

        clean_data.append(clean_game)
    

    if team :
        clean_data = [g for g in clean_data if g["home_team"]["tricode"] == team.upper() or g["away_team"]["tricode"] == team.upper()]


    return jsonify(clean_data)

@games_bp.route("/standings")
@limiter.limit("5 per minute")
@cache.cached(timeout=3600, query_string=True)
def standings():    

    """
    Obtiene la tabla de posiciones (Standings) por conferencia.
    ---
    parametros:
      - name: season
        in: query
        type: string
        required: true
        description: Temporada a consultar. Ej. 2023-24
    respuestas:
      200:
        description: Tabla de posiciones dividida en 'east' y 'west', ordenada por porcentaje de victorias.
      400:
        description: Falta el parámetro de temporada.
    """

    season = request.args.get("season")

    if not season:
        return jsonify({"Error " : "Se necesita de la temporada para ver la informacion"}),400
    
    data = fetch_standings(season=season)

    if not data:
        return jsonify({"Error" : "No existe informacion de lo que busca"}),404
    
    
    east = []
    west = []

    for d in data:
        team_stats  = {
            "team" : d["TeamCity"] + " " + d["TeamName"],
            "wins" : d["WINS"],
            "loses" : d["LOSSES"],
            "win_pct" : d["WinPCT"],
        }
        
        if d["Conference"] == "East":
            east.append(team_stats)
        else:
            west.append(team_stats)    

    east = sorted(east,key = lambda x: x["win_pct"],reverse=True)
    west = sorted(west,key = lambda x: x["win_pct"],reverse=True)

    return jsonify({"east" : east,"west" : west})
          

@games_bp.route("/boxScore/<game_id>")
@limiter.limit("15 per minute")
@cache.cached(timeout=60, query_string=True)
def box_score(game_id):

    """
    Obtiene las estadísticas detalladas y líderes individuales de un juego.
    ---
    parametros:
      - name: game_id
        in: path
        type: string
        required: true
        description: ID único del juego. Ej. 0042300401
    respuestas:
      200:
        description: Estadísticas de líderes en puntos, asistencias y rebotes para ambos equipos.
      404:
        description: ID de juego no encontrado o estadísticas no disponibles aún.
      500:
        description: Error al calcular los líderes del partido.
    """

    if not game_id or len(game_id)<5:
        return jsonify({"Error" : "El Id del partido es invalido"}),400    

    raw_data = fetch_box_score(game_id = game_id)      

    if not raw_data or "homeTeam" not in raw_data or "awayTeam" not in raw_data:
        return jsonify({"Error" : "Estadisticas no encontradas para este Id"}),404
    
    home_players = raw_data["homeTeam"]["players"]
    away_players = raw_data["awayTeam"]["players"]

    if not home_players or not away_players:
        return jsonify({"Error" : "Datos insuficientes", "Mensaje" : "El partido podría estar programado pero aún no tiene estadisticas de jugadores"}),404
    
    top_scorer_home_team = get_top_stat(home_players,"points")
    top_scorer_away_team = get_top_stat(away_players,"points")
    top_assister_home_team = get_top_stat(home_players,"assists")
    top_assister_away_team = get_top_stat(away_players,"assists")
    top_rebounder_home_team = get_top_stat(home_players,"reboundsTotal")
    top_rebounder_away_team = get_top_stat(away_players,"reboundsTotal")

    leaders =  [top_scorer_home_team,top_scorer_away_team,top_assister_home_team,top_assister_away_team,top_rebounder_home_team,top_rebounder_away_team]
    if any(l is None for l in leaders):
        return jsonify ({"Error" : "No se pudieron calcular los lideres del partido"}),500
    
    return jsonify({
        "home_team": {
            "top_scorer": {"name": top_scorer_home_team["firstName"] + " " + top_scorer_home_team["familyName"], "points": top_scorer_home_team["statistics"]["points"]},
            "top_assister": {"name": top_assister_home_team["firstName"] + " " + top_assister_home_team["familyName"], "assists": top_assister_home_team["statistics"]["assists"]},
            "top_rebounder": {"name": top_rebounder_home_team["firstName"] + " " + top_rebounder_home_team["familyName"], "rebounds": top_rebounder_home_team["statistics"]["reboundsTotal"]}
        },
        "away_team": {
            "top_scorer": {"name": top_scorer_away_team["firstName"] + " " + top_scorer_away_team["familyName"], "points": top_scorer_away_team["statistics"]["points"]},
            "top_assister": {"name": top_assister_away_team["firstName"] + " " + top_assister_away_team["familyName"], "assists": top_assister_away_team["statistics"]["assists"]},
            "top_rebounder": {"name": top_rebounder_away_team["firstName"] + " " + top_rebounder_away_team["familyName"], "rebounds": top_rebounder_away_team["statistics"]["reboundsTotal"]}
        }
    })

