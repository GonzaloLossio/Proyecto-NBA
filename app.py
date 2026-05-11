from flask import Flask
from routes.players import players_bp
from routes.games import games_bp
from routes.auth import auth_bp
from extensions import cache, limiter,db,bcrypt,login_manager
from errors import register_error_handlers
from flasgger import Swagger
from models.favorite import Favorite
from models.user import User


app = Flask(__name__)
cache.init_app(app, config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300})
limiter.init_app(app)
swagger = Swagger(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///basketball.db"
app.config['SECRET_KEY'] = '24c089ed4399a2bc19916bc9'

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

register_error_handlers(app)

app.register_blueprint(players_bp)
app.register_blueprint(games_bp)
app.register_blueprint(auth_bp)

@app.route('/')
def index():
    return app.send_static_file("index.html")


if __name__ in '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug = True)