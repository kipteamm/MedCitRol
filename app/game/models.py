from app.extensions import db

from sqlalchemy.sql import func
from sqlalchemy import DateTime

from datetime import datetime, timezone, timedelta

import random
import string
import uuid


initial_current_time = datetime(1100, 5, 8, 6, 0, 0, tzinfo=timezone.utc)


def get_uuid():
    return str(uuid.uuid4())


class World(db.Model):
    __tablename__ = 'world'

    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    user_id = db.Column(db.String(128), db.ForeignKey('users.id'), nullable=False) # world owner
    name = db.Column(db.String(50), default="Unnamed")
    code = db.Column(db.String(10), nullable=False)

    task_index = db.Column(db.Integer, default=0)

    current_time = db.Column(db.DateTime, default=initial_current_time, nullable=False)
    last_time_update = db.Column(DateTime(timezone=True), default=func.now())

    def __init__(self, user_id):
        self.user_id = user_id
        self.last_time_update = datetime.now()
        
        while True:
            code = ''.join(random.choices(string.ascii_letters, k=16))

            if not World.query.filter_by(code=code).first():
                self.code = code

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


def get_seed():
    return random.randint(0, 9999999999)


class Settlement(db.Model):
    __tablename__ ='settlement'

    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    world_id = db.Column(db.String(128), db.ForeignKey('world.id'), nullable=False)
    seed = db.Column(db.Integer, nullable=False, default=get_seed)

    name = db.Column(db.String(120), nullable=False)
    colour = db.Column(db.String(120), nullable=False)
    hallmark = db.Column(db.Boolean, default=False)

    taxes = db.Column(db.Integer, default=0)
    value_economy = db.Column(db.Integer, default=0)
    citizens = db.Column(db.Boolean, default=False)

    traderoutes = db.Column(db.Text, default="[]")

    revolution = db.Column(db.Boolean, default=False)
    start_revolution = db.Column(DateTime(timezone=True), default=None)


class SettlementRuler(db.Model):
    __tablename__ = 'settlement_ruler'

    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    settlement_id = db.Column(db.String(128), db.ForeignKey('settlement.id'), nullable=False)

    name = db.Column(db.String(120), nullable=False)
    surname = db.Column(db.String(120), nullable=False)

    # characteristics
    tyranny = db.Column(db.Integer, default=0)
    economy = db.Column(db.Integer, default=0)
    religion = db.Column(db.Integer, default=0)
    social = db.Column(db.Integer, default=0)
    military = db.Column(db.Integer, default=0)

    actions = db.Column(db.Text, default="[]")
    last_action = db.Column(db.Text, default="")
    last_action_date = db.Column(db.DateTime, default=None)


class TraderouteRequest(db.Model):
    __tablename__ = 'traderoute_request'

    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    settlement_id = db.Column(db.String(128), db.ForeignKey('settlement.id'), nullable=False)
    traderoute_id = db.Column(db.String(128), db.ForeignKey('settlement.id'), nullable=False)
    traderoute_taxes = db.Column(db.Integer, default=0)


class Character(db.Model):
    __tablename__ = 'character'

    # identification
    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    user_id = db.Column(db.String(128), db.ForeignKey('users.id'), nullable=False)
    world_id = db.Column(db.String(128), db.ForeignKey('world.id'), nullable=False)
    settlement_id = db.Column(db.String(128), db.ForeignKey('settlement.id'), nullable=False)
    last_update = db.Column(DateTime(timezone=True), default=None)

    name = db.Column(db.String(120))
    surname = db.Column(db.String(120))

    # properties
    hunger = db.Column(db.Integer, default=30)
    fatigue = db.Column(db.Integer, default=20)
    health = db.Column(db.Float, default=30)
    happiness = db.Column(db.Integer, default=15)
    pennies = db.Column(db.Integer, default=12)
    taxes = db.Column(db.Integer, default=0)
    house_id = db.Column(db.Integer)
    
    profession = db.Column(db.String(120))
    task_index = db.Column(db.Integer, default=0)

    start_sleep = db.Column(DateTime(timezone=True), default=None)

    jailed = db.Column(db.Boolean, default=False)
    jail_end = db.Column(DateTime(timezone=True), default=None)
    freedom_request = db.Column(DateTime(timezone=True), default=None)
    revolutionary = db.Column(db.Boolean, default=False)


class AccessKey(db.Model):
    __tablename__ = 'access_key'

    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    user_id = db.Column(db.String(128), db.ForeignKey('users.id'), nullable=False)
    world_id = db.Column(db.String(128), db.ForeignKey('world.id'), nullable=False)
    settlement_id = db.Column(db.String(128), db.ForeignKey('settlement.id'))
    character_id = db.Column(db.String(128), db.ForeignKey('character.id'))

    key = db.Column(db.String(128))
    key_date = db.Column(DateTime(timezone=True), default=func.now(), nullable=False)
    

class Tile(db.Model):
    __tablename__ = 'tile'

    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    character_id = db.Column(db.String(128), db.ForeignKey('character.id'))
    settlement_id = db.Column(db.String(128), db.ForeignKey('settlement.id'), nullable=False)

    pos_x = db.Column(db.Integer, nullable=False)
    pos_y = db.Column(db.Integer, nullable=False)

    tile_type = db.Column(db.String(128))
    future = db.Column(db.String(128))
    

class InventoryItem(db.Model):
    __tablename__ = 'inventory_item'

    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    settlement_id = db.Column(db.String(128), db.ForeignKey('settlement.id'), nullable=False)
    character_id = db.Column(db.String(128), db.ForeignKey('character.id'))
    warehouse_id = db.Column(db.String(128), db.ForeignKey('warehouse.id'))

    item_type = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Integer, default=0)
    buildable = db.Column(db.Boolean, default=False)


class Farmer(db.Model):
    __tablename__ = 'farmer'

    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    character_id = db.Column(db.String(128), db.ForeignKey('character.id'), nullable=False)

    date = db.Column(db.DateTime, nullable=False)
    stage = db.Column(db.String(120), default="farm_land", nullable=False)


class MarketItem(db.Model):
    __tablename__ = 'market_item'

    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    character_id = db.Column(db.String(128), db.ForeignKey('character.id'), nullable=False)
    world_id = db.Column(db.String(128), db.ForeignKey('world.id'))
    settlement_id = db.Column(db.String(128), db.ForeignKey('settlement.id'), nullable=False)

    item_type = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Integer, default=0)
    price = db.Column(db.Integer, default=0)


class Merchant(db.Model):
    __tablename__ = 'merchant'

    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    settlement_id = db.Column(db.String(128), db.ForeignKey('settlement.id'), nullable=False)
    name = db.Column(db.String(120), default="Zita")
    surname = db.Column(db.String(120), default="Wainwright")

    merchant_type = db.Column(db.String(120), nullable=False)

    end_date = db.Column(db.DateTime, nullable=False)


class Warehouse(db.Model):
    __tablename__ = 'warehouse'

    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    settlement_id = db.Column(db.String(128), db.ForeignKey('settlement.id'), nullable=False)
    tile_id = db.Column(db.String(128), db.ForeignKey('tile.id'), nullable=False)

    capacity = db.Column(db.Integer, default=0)