from app.utils.serializers import tile_serializer
from app.utils.functions import generateRandomCoordinates
from app.utils.rulers import Ruler
from app.game.models import World, Settlement, Character, Tile, Merchant
from app.auth.models import User
from app.extensions import db, socketio

from datetime import timedelta

import random
import json


with open('app/static/data/names.json') as names_file:
    NAMES_DATA = json.load(names_file)

with open('app/static/data/surnames.json') as surnames_file:
    SURNAMES_DATA = json.load(surnames_file)

with open('app/static/data/city_names.json') as city_names_file:
    CITY_NAMES_DATA = json.load(city_names_file)

# Function to get a random name
def _get_random_name():
    return random.choice(NAMES_DATA)

# Function to get a random surname
def _get_random_surname():
    return random.choice(SURNAMES_DATA)

def _get_random_city_name():
    return random.choice(CITY_NAMES_DATA)


def _create_settlement(world: World, colour: str) -> Settlement:
    settlement = Settlement(world_id=world.id, name=_get_random_city_name(), colour=colour)

    db.session.add(settlement)
    db.session.commit()

    Ruler().create(settlement.id)

    tile = Tile(settlement_id=settlement.id, pos_x=37, pos_y=37, tile_type="well")
            
    db.session.add(tile)
    db.session.commit()

    merchant = Merchant(settlement_id=settlement.id, name=_get_random_name(), surname=_get_random_surname(), merchant_type="grain", end_date=(world.current_time + timedelta(weeks=8)))

    db.session.add(merchant)
    db.session.commit()

    return settlement


settlement_colours = ['cyan', 'lime', 'purple', 'red', 'brown']


def _get_settlement(world: World) -> Settlement:
    settlements = Settlement.query.filter_by(world_id=world.id).all()

    if not settlements:
        return _create_settlement(world, settlement_colours[0])

    if len(settlements) < len(settlement_colours):
        for i, settlement in enumerate(settlements):
            if Character.query.filter_by(world_id=world.id, settlement_id=settlement.id).count() < 8:
                return settlement

        return _create_settlement(world, settlement_colours[len(settlements)])
    
    smallest_settlement = min(settlements, key=lambda s: Character.query.filter_by(world_id=world.id, settlement_id=s.id).count())

    return smallest_settlement


def _create_character(world: World, user: User, settlement: Settlement) -> Character:
    character = Character(world_id=world.id, user_id=user.id, settlement_id=settlement.id, name=_get_random_name(), surname=_get_random_surname())

    db.session.add(character)
    db.session.commit()

    pos_x, pos_y = None, None

    while pos_x is None or pos_y is None:
        pos_x, pos_y = generateRandomCoordinates(29, 35, 5, True, settlement.id)

    house = Tile(character_id=character.id, settlement_id=settlement.id, pos_x=pos_x, pos_y=pos_y, tile_type="hut")

    db.session.add(house)
    db.session.commit()

    character.house_id = house.id

    socketio.emit("new_tiles", [tile_serializer(house)], room=settlement.id) # type: ignore

    return character

def _update_character(character: Character, world: World):
    if character.jailed and world.current_time >= character.jail_end:
        character.jailed = False
        character.jail_end = None

    if character.last_update:
        hours_passed = round((world.current_time - character.last_update).total_seconds() / 3600)

    else:
        return

    if character.hunger > 0:
        character.hunger -= min(hours_passed, 16)
        character.hunger = max(character.hunger, 0) 
            
    if character.health > 0:
        character.health -= min(hours_passed * 0.25, 16)
        character.health = max(character.health, 0) 

    if character.fatigue > 0:
        character.fatigue -= min(hours_passed, 16)
        character.fatigue = max(character.fatigue, 0) 
                
    character.last_update = world.current_time

    db.session.commit()

    return


def get_presence(world: World, user: User) -> tuple[Settlement, Character]:
    user.active_world = world.id

    db.session.commit()

    character = Character.query.filter_by(world_id=world.id, user_id=user.id).first()

    if not character:
        settlement = _get_settlement(world)
        character = _create_character(world, user, settlement)

    else:
        settlement = Settlement.query.filter_by(world_id=world.id, id=character.settlement_id).first()

        _update_character(character, world)

    return settlement, character
