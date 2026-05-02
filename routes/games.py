from flask import Blueprint,request,jsonify
from services.games_api_client import fetch_scoreboard, fetch_standings

games_bp = Blueprint("games",__name__)


@games_bp.route("/scoreboard")
def scoreboard():
    game_date = request.args.get("game_date")
    team = request.args.get("team")

    if not game_date:
        return jsonify({"Error" : "Se necesita una fecha para buscar los juegos"}),400
    
    game = fetch_scoreboard(game_date=game_date)

    if not game:
        return jsonify({"Error" : "No se han encontrado partidos en la fecha indicada"}),404
    
    clean_data = []
    clean_data = [{
        "game_id" : g["gameId"],
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
        "home_leaders" : {
            "name" : g["gameLeaders"]["homeLeaders"]["name"],
            "points" : g["gameLeaders"]["homeLeaders"]["points"],
            "assists" : g["gameLeaders"]["homeLeaders"]["assists"],
            "rebounds" : g["gameLeaders"]["homeLeaders"]["rebounds"],
        },
        "away_leaders" : {
            "name" : g["gameLeaders"]["awayLeaders"]["name"],
            "points": g["gameLeaders"]["awayLeaders"]["points"],
            "assists": g["gameLeaders"]["awayLeaders"]["assists"],
            "rebounds": g["gameLeaders"]["awayLeaders"]["rebounds"],
        },
        "status" : g["gameStatusText"],
    }for g in game]

    if team :
        clean_data = [g for g in clean_data if g["home_team"]["tricode"] == team.upper() or g["away_team"]["tricode"] == team.upper()]


    return jsonify(clean_data)

@games_bp.route("/standings")
def standings():    
    season = request.args.get("season")

    if not season:
        return jsonify({"Error " : "Se necesita de la temporada para ver la informacion"}),400
    
    data = fetch_standings(season=season)

    if not data:
        return jsonify({"Error" : "No existe informacion de lo que busca"}),404
    
    clean_data = []
    east = []
    west = []

    for d in data:
        clean_data  = {
            "team" : d["TeamCity"] + " " + d["TeamName"],
            "wins" : d["WINS"],
            "loses" : d["LOSSES"],
            "win_pct" : d["WinPCT"],
        }
        
        if d["Conference"] == "East":
            east.append(clean_data)
        else:
            west.append(clean_data)    

    east = sorted(east,key = lambda x: x["win_pct"],reverse=True)
    west = sorted(west,key = lambda x: x["win_pct"],reverse=True)

    return jsonify({"east" : east,"west" : west})
          