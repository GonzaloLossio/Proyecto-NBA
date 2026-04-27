from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

from routes.players import players_bp
app.register_blueprint(players_bp,url_prefix='/api/players')

@app.route('/')
def index():
    return app.send_static_file('index.html')


if __name__ in "__main__":
    app.run(debug=True)