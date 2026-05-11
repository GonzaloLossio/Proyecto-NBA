from flask_login import current_user,login_required
from flask import Blueprint,request,jsonify
from extensions import db
from models.favorite import Favorite

favorites_bp = Blueprint("favorites",__name__)

@favorites_bp.route("/favorites", methods = ["POST"])
@login_required
def add_favorite():
    data = request.get_json()

    player_id = data.get("player_id")
    player_name = data.get("player_name")

    if not player_id or not player_name :
        return jsonify({"Error" : "Se requiere el id del jugador y el nombre del jugador"}),400
    
    existing = Favorite.query.filter_by(user_id = current_user.id,player_id = player_id).first()
    
    if existing:
        return jsonify({"Mensaje" : f"El jugador {player_name} ya se encuentra en sus favoritos"}),409
    
    new_favorite = Favorite(player_id = player_id, player_name = player_name,user_id = current_user.id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"Mensaje" : f"{player_name} agregado a favoritos"}),201


@favorites_bp.route("/favorites", methods = ["GET"])
@login_required
def get_favorites():
    favorites = Favorite.query.filter_by(user_id = current_user.id).all()

    result = [{
        "player_id" : f.player_id,
        "player_name" : f.player_name,
        "created_at" : f.created_at,
    }for f in favorites]

    return jsonify(result),200

@favorites_bp.route("/favorites/<int:player_id>", methods = ["DELETE"])
@login_required
def delete_favorites(player_id):
    data  = request.get_json()
    player_name = data.get("player_name")
    favorite = Favorite.query.filter_by(user_id = current_user.id, player_id = player_id).first()

    if not favorite:
        return jsonify({"Error" : f"El jugador {player_name} no se encuentra en sus favoritos "}),404
    
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"Mensaje" : f"El jugador {player_name} fue eliminado con exito"}),200