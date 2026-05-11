from extensions import login_manager,db,bcrypt
from datetime import datetime

class Favorite(db.Model):
    id = db.Column(db.Integer(),primary_key = True)
    player_id = db.Column(db.Integer(),nullable = False)
    player_name = db.Column(db.String(),nullable = False)
    created_at = db.Column(db.DateTime(),default = datetime.utcnow)
    user_id = db.Column(db.Integer(),db.ForeignKey("user.id"),nullable = False)