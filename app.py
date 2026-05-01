from flask import Flask
from routes.players import players_bp
from routes.games import games_bp
from extensions import cache
from errors import register_error_handlers

app = Flask(__name__)
cache.init_app(app, config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300})
register_error_handlers(app)

app.register_blueprint(players_bp)
app.register_blueprint(games_bp)


@app.route('/')
def index():
    return app.send_static_file("index.html")


if __name__ in "__main__":
    app.run(debug = True)