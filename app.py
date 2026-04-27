from flask import Flask
from routes.players import players_bp
from routes.games import games_bp

app = Flask(__name__)

app.register_blueprint(players_bp)
app.register_blueprint(games_bp)


@app.route('/')
def index():
    return app.send_static_file("index.html")


if __name__ in "__main__":
    app.run(debug = True)