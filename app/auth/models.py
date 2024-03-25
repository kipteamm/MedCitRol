from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    # Authentication
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    worlds = db.relationship('World', secondary='user_worlds', backref=db.backref('users', lazy='dynamic'))

    def __init__(self, email, password):
        self.email = email
        self.set_password(password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def authenticate(email, password):
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            return user
        return None


class UserWorlds(db.Model):
    __tablename__ = 'user_worlds'

    world_id = db.Column(db.Integer, db.ForeignKey('world.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
