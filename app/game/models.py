from app.extensions import db

from sqlalchemy.sql import func
from sqlalchemy import DateTime

from datetime import datetime, timezone, timedelta

from app.utils.tiles import get_tile_index

import random
import string


initial_current_time = datetime(1100, 5, 8, 0, 0, 0, tzinfo=timezone.utc)


class World(db.Model):
    __tablename__ = 'world'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # world owner
    code = db.Column(db.String(10), nullable=False)

    question_index = db.Column(db.Integer, default=0)

    current_time = db.Column(db.DateTime, default=initial_current_time, nullable=False)
    last_time_update = db.Column(DateTime(timezone=True), default=func.now())

    def __init__(self, user_id):
        self.user_id = user_id
        self.last_time_update = datetime.now()
        
        while True:
            room_id = ''.join(random.choices(string.ascii_letters, k=16))

            if not World.query.filter_by(code=room_id).first():
                self.code = room_id

                break

    def update_time(self) -> None:
        if self.last_time_update is None:
            self.last_time_update = func.now()
            db.session.commit()
            return

        time_difference = (datetime.now() - self.last_time_update).total_seconds() // 60

        self.current_time += timedelta(hours=time_difference)
        self.last_time_update += timedelta(minutes=time_difference) # type: ignore

        db.session.commit()

    def get_world_time(self) -> int:
        reference_date = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        date = datetime(self.current_time.year, self.current_time.month, self.current_time.day, self.current_time.hour, 0, 0, tzinfo=timezone.utc)
        
        delta = date - reference_date
        
        return int(delta.total_seconds())

    def get_dict(self) -> dict:
        return {
            'id' : self.id,
            'user_id' : self.id,
            'code' : self.code,
            'current_time' : self.get_world_time()
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

    house_id = db.Column(db.Integer)
    
    profession = db.Column(db.String(120))
    task_index = db.Column(db.Integer, default=0)

    def get_dict(self) -> dict:
        return {
            'id' : self.id,
            'user_id' : self.user_id,
            'world_id' : self.world_id,
            'settlement_id' : self.settlement_id,
            'house_id' : self.house_id,
            'profession' : self.profession,
            'task_index' : self.task_index 
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
    

class Tile(db.Model):
    __tablename__ = 'tile'

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'))
    settlement_id = db.Column(db.Integer, db.ForeignKey('settlement.id'), nullable=False)

    pos_x = db.Column(db.Integer, nullable=False)
    pos_y = db.Column(db.Integer, nullable=False)

    tile_type = db.Column(db.String(128))

    def get_dict(self) -> dict:
        return {
            'id' : self.id,
            'settlement_id' : self.settlement_id,
            'pos_x' : self.pos_x,
            'pos_y' : self.pos_y,
            'tile_type' : self.tile_type,
            'tile_index' : get_tile_index(self.tile_type),
        }
    