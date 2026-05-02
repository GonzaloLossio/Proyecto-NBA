from flask import Blueprint,request,jsonify
from services.games_api_client import fetch_scoreboard

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