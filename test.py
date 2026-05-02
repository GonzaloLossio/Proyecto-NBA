from nba_api.stats.endpoints import scoreboardv3
from datetime import date

scoreboard = scoreboardv3.ScoreboardV3(game_date="2024-04-14")
data = scoreboard.get_dict()
games = data["scoreboard"]["games"]
game = games[0]
print("homeTeam:", game["homeTeam"].keys())
print("gameLeaders:", game["gameLeaders"].keys())
print("homeLeaders:", game["gameLeaders"]["homeLeaders"].keys())
print(games[0].keys())