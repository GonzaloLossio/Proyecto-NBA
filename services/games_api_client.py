from nba_api.stats.endpoints import scoreboardv3
from nba_api.stats.endpoints import leaguestandingsv3
from datetime import date

def fetch_scoreboard(game_date=None):
    if not game_date:
        game_date = date.today().isoformat()

    scoreboard = scoreboardv3.ScoreboardV3(game_date=game_date)
    data = scoreboard.get_dict()
    games = data["scoreboard"]["games"]

    return games

def fetch_standings(season = None):
    standings = leaguestandingsv3.LeagueStandingsV3(season=season)
    data = standings.get_normalized_dict()
    return data["Standings"]
