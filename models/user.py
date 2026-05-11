from extensions import login_manager,db,bcrypt
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer(),primary_key = True)
    username = db.Column(db.String(length  = 20),nullable = False, unique = True)
    password = db.Column(db.String(length  = 60),nullable = False)
    email = db.Column(db.String(),nullable = False)
    favorites = db.relationship("Favorite",backref = "user",lazy = True)
