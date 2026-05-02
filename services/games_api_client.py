from nba_api.stats.endpoints import scoreboardv3
from datetime import date

def fetch_scoreboard(game_date=None):
    if not game_date:
        game_date = date.today().isoformat()

    scoreboard = scoreboardv3.ScoreboardV3(game_date=game_date)
    data = scoreboard.get_dict()
    games = data["scoreboard"]["games"]

    return games