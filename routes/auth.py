from flask import Blueprint,jsonify,request
from extensions import bcrypt,db
from models.user import User
from flask_login import login_user,logout_user

auth_bp = Blueprint("auth",__name__)

@auth_bp.route("/register",methods = ["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"Error" : "Todos los campos son obligatorios"}),400
    
    if User.query.filter_by(email = email).first():
        return jsonify({"Error" : "Email ya esta registrado"}),201
    
    if User.query.filter_by(username = username).first():
        return jsonify({"Error" : "Usuario ya existe"}),201

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    new_user = User(username=username,email=email,password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"Mensaje" : f"Usuario {username} creado exitosamente"}),201

@auth_bp.route("/login",methods = ["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username = username).first()

    if not user : 
        return jsonify({"Error" : "Usuario no existe"}),404
    
    if not bcrypt.check_password_hash(user.password,password):
        return jsonify({"Error" : "Contraseña incorrecta"}),401
    
    login_user(user)
    return jsonify({"Mensaje":f"Bienvenido {username}"}),200

@auth_bp.route("/logout",methods = ["POST"])
def logout():
    logout_user()
    return jsonify({"Mensaje" : "Sesion cerrada correctamente"}),200