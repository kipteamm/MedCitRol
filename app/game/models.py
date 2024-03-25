from app.extensions import db

from datetime import datetime, timezone

import random
import string


class World(db.Model):
    __tablename__ = 'world'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # world owner
    code = db.Column(db.String(10), nullable=False)

    current_time = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)

    def __init__(self, user_id):
        self.user_id = user_id
        
        
        while True:
            room_id = ''.join(random.choices(string.ascii_letters, k=10))

            if not World.query.filter_by(code=room_id).first():
                self.code = room_id

                break


class Settlement(db.Model):
    __tablename__ ='settlement'

    id = db.Column(db.Integer, primary_key=True)
    world_id = db.Column(db.Integer, db.ForeignKey('world.id'), nullable=False)

    name = db.Column(db.String(120), nullable=False)


class Character(db.Model):
    __tablename__ = 'character'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    world_id = db.Column(db.Integer, db.ForeignKey('world.id'), nullable=False)
    settlement_id = db.Column(db.Integer, db.ForeignKey('settlement.id'), nullable=False)
