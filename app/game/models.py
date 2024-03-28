from app.extensions import db

from sqlalchemy.sql import func
from sqlalchemy import DateTime

from datetime import datetime, timezone

import random
import string


class World(db.Model):
    __tablename__ = 'world'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # world owner
    code = db.Column(db.String(10), nullable=False)

    initial_current_time = datetime(1100, 5, 8, 0, 0, 0, tzinfo=timezone.utc)
    current_time = db.Column(db.DateTime, default=initial_current_time, nullable=False)

    def __init__(self, user_id):
        self.user_id = user_id
        
        
        while True:
            room_id = ''.join(random.choices(string.ascii_letters, k=10))

            if not World.query.filter_by(code=room_id).first():
                self.code = room_id

                break

    def get_dict(self) -> dict:
        return {
            'id' : self.id,
            'user_id' : self.id,
            'code' : self.code,
            'current_time' : self.current_time
        }


class Settlement(db.Model):
    __tablename__ ='settlement'

    id = db.Column(db.Integer, primary_key=True)
    world_id = db.Column(db.Integer, db.ForeignKey('world.id'), nullable=False)

    name = db.Column(db.String(120), nullable=False)
    colour = db.Column(db.String(120), nullable=False)

    def get_dict(self) -> dict:
        return {
            'id' : self.id,
            'world_id' : self.world_id,
            'name' : self.name,
            'colour' : self.colour
        }


class Character(db.Model):
    __tablename__ = 'character'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    world_id = db.Column(db.Integer, db.ForeignKey('world.id'), nullable=False)
    settlement_id = db.Column(db.Integer, db.ForeignKey('settlement.id'), nullable=False)

    def get_dict(self) -> dict:
        return {
            'id' : self.id,
            'user_id' : self.user_id,
            'world_id' : self.world_id,
            'settlement_id' : self.settlement_id
        }


class AccessKey(db.Model):
    __tablename__ = 'access_key'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    world_id = db.Column(db.Integer, db.ForeignKey('world.id'), nullable=False)
    settlement_id = db.Column(db.Integer, db.ForeignKey('settlement.id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)

    key = db.Column(db.String(128))
    key_date = db.Column(DateTime(timezone=True), default=func.now(), nullable=False)
    