from app.utils.serializers import tile_serializer
from app.game.models import World, Settlement, Character, AccessKey, Tile
from app.auth.models import User
from app.extensions import db, socketio

from datetime import datetime, timezone, timedelta

from typing import Optional

import secrets
import random


settlement_colours = ['cyan', 'lime', 'purple', 'red', 'brown']

def get_presence(world: World, user: User) -> tuple[Settlement, Character]:
    user.active_world = world.id

    db.session.commit()

    character = Character.query.filter_by(world_id=world.id, user_id=user.id).first()

    if not character:
        settlements = Settlement.query.filter_by(world_id=world.id).all()

        if not settlements:
            settlement = Settlement(world_id=world.id, name="Unnamed", colour=settlement_colours[0])

            db.session.add(settlement)
            db.session.commit()

            tile = Tile(settlement_id=settlement.id, pos_x=37, pos_y=37, tile_type="well")
            
            db.session.add(tile)
            db.session.commit()

        elif len(settlements) < len(settlement_colours):
            i = len(settlements)

            for _settlement in settlements:
                if Character.query.filter_by(world_id=world.id, settlement_id=_settlement.id).count() >= 8:
                    settlement = Settlement(world_id=world.id, name="Unnamed", colour=settlement_colours[i])

                    db.session.add(settlement)
                    db.session.commit()

                    tile = Tile(settlement_id=settlement.id, pos_x=37, pos_y=37, tile_type="well")
                    
                    db.session.add(tile)
                    db.session.commit()

                    break

                settlement = _settlement

                i += 1

                break
        else:
            character_counts = []

            for i in range(settlements):
                character_counts[i] = {
                    'characters' : Character.query.filter_by(world_id=world.id, settlement_id=settlements[i].id),
                    'id' : settlements[i].id
                }

            sorted_data = sorted(character_counts, key=lambda x: x['characters'])

            settlement = settlements.query.filter_by(id=sorted_data[i].id)

        character = Character(world_id=world.id, user_id=user.id, settlement_id=settlement.id)

        db.session.add(character)
        db.session.commit()

        pos_x, pos_y = None, None

        while pos_x is None or pos_y is None:
            pos_x, pos_y = generateRandomCoordinates(37, 37, 5, True, settlement.id)

        house = Tile(character_id=character.id, settlement_id=settlement.id, pos_x=pos_x, pos_y=pos_y, tile_type="hut")

        db.session.add(house)
        db.session.commit()

        character.house_id = house.id

        socketio.emit("new_tiles", [tile_serializer(house)], room=settlement.id) # type: ignore

    else:
        settlement = Settlement.query.filter_by(world_id=world.id, id=character.settlement_id).first()

    return settlement, character


def get_key(user_id: int, world_id: Optional[int]=None, settlement_id: Optional[int]=None, character_id: Optional[int]=None) -> str:
    access_key = AccessKey.query.filter_by(user_id=user_id).first()

    now = datetime.now(timezone.utc)

    if not access_key:
        access_key = AccessKey(
            user_id=user_id, 
            world_id=world_id, 
            settlement_id=settlement_id, 
            character_id=character_id,
            key=secrets.token_hex(nbytes=64),
            key_date=now
        )

        db.session.add(access_key)
        db.session.commit()

        return access_key.key
    
    if access_key.key_date.tzinfo is None:
        access_key.key_date = access_key.key_date.replace(tzinfo=timezone.utc)

    expired = access_key.key_date - now > timedelta(hours=12) if access_key.key_date else False

    if expired or not access_key.key:
        access_key.key = secrets.token_hex(nbytes=64)
        access_key.key_date = now

        db.session.commit()

    return access_key.key


def authenticated(data: dict) -> bool:
    access_key = AccessKey.query.filter_by(world_id=data['world_id'], settlement_id=data['settlement_id'], character_id=data['character_id'], key=data['access_key']).first()

    if not access_key:
        return False
    
    return True


def generateRandomCoordinates(center_x: int, center_y: int, deviation: int, empty: bool=False, settlement_id: Optional[int]=None) -> tuple[Optional[int], Optional[int]]:
    pos_x = center_x + random.randint(-deviation, deviation)
    pos_y = center_y + random.randint(-deviation, deviation)

    if not empty:
        return pos_x, pos_y
    
    if not settlement_id:
        return None, None

    if Tile.query.filter_by(settlement_id=settlement_id, pos_x=pos_x, pos_y=pos_y).first():
        return None, None

    return pos_x, pos_y
