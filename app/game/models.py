from app.extensions import db

from datetime import datetime, timezone


class World(db.Model):
    __tablename__ = 'world'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # world owner

    current_time = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)


class Settlement(db.Model):
    __tablename__ ='settlement'

    id = db.Column(db.Integer, primary_key=True)
    world_id = db.Column(db.Integer, db.ForeignKey('world.id'), nullable=False)

    name = db.Column(db.String(120), nullable=False)


class Character(db.Model):
    __tablename__ = 'character'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    settlement_id = db.Column(db.Integer, db.ForeignKey('settlement.id'), nullable=False)
