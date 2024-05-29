from app.utils.serializers import tile_serializer, small_settlement_serializer
from app.utils.functions import generateRandomCoordinates
from app.utils.rulers import Ruler
from app.game.models import World, Settlement, SettlementRuler, Character, Tile, Merchant
from app.auth.models import User
from app.extensions import db, socketio

from datetime import timedelta, datetime

import random
import json


MIN_CHARACTERS = 8


with open('app/static/data/names.json') as names_file:
    NAMES_DATA = json.load(names_file)

with open('app/static/data/surnames.json') as surnames_file:
    SURNAMES_DATA = json.load(surnames_file)

with open('app/static/data/city_names.json') as city_names_file:
    CITY_NAMES_DATA = json.load(city_names_file)


def _get_random_name():
    return random.choice(NAMES_DATA)


def _get_random_surname():
    return random.choice(SURNAMES_DATA)


def _get_random_city_name():
    return random.choice(CITY_NAMES_DATA)


def add_merchant(settlement_id: str, current_time: datetime, weeks: int, allow_miscellaneous: bool=False) -> None:
    merchant_type = "grain"
    
    if allow_miscellaneous and random.randint(1, 2) == 1:
        merchant_type = "miscellaneous"

    merchant = Merchant(settlement_id=settlement_id, name=_get_random_name(), surname=_get_random_surname(), merchant_type=merchant_type, end_date=(current_time + timedelta(weeks=weeks)))

    db.session.add(merchant)
    db.session.commit()

    return


def _create_settlement(world: World, colour: str) -> Settlement:
    settlement = Settlement(world_id=world.id, name=_get_random_city_name(), colour=colour)

    db.session.add(settlement)
    db.session.commit()

    Ruler().create(settlement.id)

    tile = Tile(settlement_id=settlement.id, pos_x=37, pos_y=37, tile_type="well")
            
    db.session.add(tile)
    db.session.commit()

    add_merchant(settlement.id, world.current_time, 8, False)

    socketio.emit('new_settlement', small_settlement_serializer(settlement), room=world.id) # type: ignore

    return settlement


SETTLEMENT_COLOURS = ['cyan', 'lime', 'purple', 'red']


def _get_settlement(world: World) -> Settlement:
    settlements = Settlement.query.filter_by(world_id=world.id).all()

    if not settlements:
        return _create_settlement(world, SETTLEMENT_COLOURS[0])

    if len(settlements) < len(SETTLEMENT_COLOURS):
        for i, settlement in enumerate(settlements):
            if Character.query.filter_by(world_id=world.id, settlement_id=settlement.id).count() < MIN_CHARACTERS:
                return settlement

        return _create_settlement(world, SETTLEMENT_COLOURS[len(settlements)])
    
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


def _update_property(character: Character, property_name: str, hours_passed: int=1) -> None:
    property_value = getattr(character, property_name)

    if property_value <= 0:
        return

    property_value -= min(hours_passed, 16)

    if property_value < 0:
        character.health = max(character.health + property_value, 0)

        property_value = 0

    setattr(character, property_name, property_value)


def update_character(character: Character, world: World, hours_passed: int=0):
    if character.jailed:
        if world.current_time >= character.jail_end:
            character.jailed = False
            character.jail_end = None

        db.session.commit()

        return
    
    if hours_passed == 0:
        if not character.last_update:
            return
    
        hours_passed = round((world.current_time - character.last_update).total_seconds() / 3600)

    if character.start_sleep:
        if world.current_time.hour < 5 or world.current_time.hour >= 20:
            return
        
        hours_slept = min((world.current_time - character.start_sleep).total_seconds() / 3600, 9)

        if hours_slept >= 6:
            character.fatigue += 18

        else:
            character.fatigue += 6 + hours_slept

            socketio.emit("alert", {'id' : character.id, 'type' : "info", 'message' : f"You did not sleep enough ({int(7 - hours_slept)} hours too little)."})

        character.start_sleep = None
        
        if character.health < 18:
            character.health += 6

        hours_passed -= hours_slept

        db.session.commit()

        if hours_passed < 1:
            return
        
    _update_property(character, "hunger", hours_passed)
    _update_property(character, "fatigue", hours_passed)
                
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

        update_character(character, world)

    return settlement, character


def update_time(world: World) -> None:
    world.current_time += timedelta(hours=1)
    world.last_time_update = datetime.now()

    db.session.commit()


def update_settlement(character: Character, world: World) -> None:
    settlement_ruler = SettlementRuler.query.filter_by(settlement_id=character.settlement_id).first()

    Ruler(settlement_ruler).work(world.current_time)

    merchant = Merchant.query.filter_by(settlement_id=character.settlement_id).first()

    if merchant and merchant.end_date < world.current_time:
        db.session.delete(merchant)

        socketio.emit("merchant_leave", room=character.settlement_id) # type: ignore

    elif not merchant and random.randint(1, 3) == 2:
        add_merchant(character.settlement_id, world.current_time, random.randint(1, 2), True)

    settlement = Settlement.query.filter(Settlement.id == character.settlement_id, Settlement.revolution == True, Settlement.start_revolution + timedelta(days=1) <= world.current_time).first()

    if not settlement:
        return
                    
    if random.random() < Character.query.filter_by(settlement_id=settlement.id, revolutionary=True).count() / Character.query.filter_by(settlement_id=settlement.id).count():
        settlement.revolution = False
        settlement.start_revolution = None

        db.session.delete(settlement_ruler)
        db.session.commit()

        Ruler().create(settlement.id)

        socketio.emit('alert', {'type' : "sucess", 'message' : "The revolution has ended and a new ruler has been chosen"}, room=character.settlement_id) #type: ignore

        for character in Character.query.filter_by(settlement_id=settlement.id, revolutionary=True).all():
            character.revolutionary = False

        db.session.commit()

        return

    for character in Character.query.filter_by(settlement_id=settlement.id, revolutionary=True).all():
        character.jailed = True
        character.jail_end = world.current_time + timedelta(hours=random.randint(12, 24))
        character.taxes = 0
        character.happiness -= max(0, character.happiness - 6)

        socketio.emit('alert', {'type' : "error", 'id' : character.id,'message' : "The revolution failed."}, room=character.settlement_id) #type: ignore

    db.session.commit()
