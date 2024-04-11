from flask import Blueprint, request, make_response, g

from app.utils.serializers import market_item_serializer, task_serializer, properties_serializer
from app.utils.professions import Profession
from app.utils.decorators import character_auhtorized
from app.utils.properties import Properties
from app.utils.inventory import Inventory
from app.teacher.models import Task
from app.game.models import Settlement, Character, MarketItem, World

from app.extensions import db, socketio

from datetime import timedelta

import math


api_blueprint = Blueprint('api', __name__, url_prefix="/api")


@api_blueprint.route("/task", methods=["GET"])
@character_auhtorized
def task(): 
    access_key = g.access_key
    character = g.character

    if not character.profession:
        return make_response({"error" : "You have no profession."}, 400)
    
    task = Task.query.filter_by(world_id=access_key.world_id, index=character.task_index).first()
    
    if not task:
        return make_response({"error": "No task found"}, 404)

    return make_response(task_serializer(task), 200)


@api_blueprint.route("/task/submit", methods=["POST"])
@character_auhtorized
def submit_task():
    access_key = g.access_key
    character = g.character

    if not character.profession:
        return make_response({"error" : "You have no profession."}, 400)
    
    task = Task.query.filter_by(world_id=access_key.world_id, index=character.task_index).first()
    
    if not task:
        return make_response({"error": "No task found"}, 404)
    
    Profession(character).work()

    return make_response(task_serializer(task), 200)


@api_blueprint.route("/profession/set", methods=["PUT"])
@character_auhtorized
def set_profession():
    json = request.json

    if not json or 'profession' not in json:
        return make_response({"error" : "Invalid profession."}, 400)
    
    profession = json['profession']

    character = g.character

    character.profession = profession

    if profession == 'farmer':
        Inventory(character.settlement_id, None, character.id).add_item('farm_land', 9)

    if profession == 'miller':
        Inventory(character.settlement_id, None, character.id).add_item('windmill', 1)

    if profession == 'baker':
        Inventory(character.settlement_id, None, character.id).add_item('bakery', 1)

    db.session.commit()

    return make_response({"success" : True}, 204)


@api_blueprint.route("/settlement/market", methods=["GET"])
@character_auhtorized
def get_settlement_market():
    access_key = g.access_key

    market_data = [market_item_serializer(market_item) for market_item in MarketItem.query.filter_by(settlement_id=access_key.settlement_id).all()]

    return make_response(market_data, 200)


@api_blueprint.route("/settlement/market/sell", methods=["POST"])
@character_auhtorized
def sell_item():
    json = request.json

    if not json or not "item_type" in json or not "amount" in json or not "price" in json:
        return make_response({"error" : "Invalid item."}, 400)
    
    access_key = g.access_key
    character = g.character
    
    inventory = Inventory(character.settlement_id, None, character.id)

    item = json["item_type"]

    try:
        amount = int(json['amount'])

    except:
        return make_response({"error" : "Invalid amount."}, 400)

    if not inventory.has_items(item_type=item, amount=amount):
        return make_response({"error" : "Invalid item."}, 400)
    
    if inventory.is_buildable(item):
        return make_response({"error" : "Invalid item."}, 400)
    
    try:
        price = int(json['price'])

    except:
        return make_response({"error" : "Invalid price."}, 400)
    
    inventory.remove_item(item_type=item, amount=amount)

    db.session.commit()

    market_item = MarketItem.query.filter_by(character_id=character.id, settlement_id=access_key.settlement_id, item_type=json["item_type"]).first()

    if not market_item:
        market_item = MarketItem(character_id=character.id, settlement_id=access_key.settlement_id, item_type=json["item_type"])

        db.session.add(market_item)
        db.session.commit()

    market_item.amount += amount
    market_item.price = price

    db.session.commit()

    return make_response(market_item_serializer(market_item), 200)  


@api_blueprint.route("/settlement/market/buy", methods=["POST"])
@character_auhtorized
def buy_item():
    json = request.json

    if not json or not "item_id" in json:
        return make_response({"error" : "Invalid item."}, 400)
    
    character = g.character
    
    item = MarketItem.query.get(json["item_id"])

    if character.pennies < item.price:
        return make_response({"error" : "You don't have enough money."}, 400)
    
    item.amount -= 1
    character.pennies -= item.price

    seller = Character.query.get(item.character_id)
    seller.pennies += item.price
    
    Inventory(character.settlement_id, None, character.id).add_item(item.item_type, 1)

    db.session.commit()

    if item.amount == 0:
        db.session.delete(item)
        db.session.commit()

    socketio.emit("update_character", properties_serializer(seller), room=seller.settlement_id) # type: ignore

    return make_response({"success" : True}, 204)


@api_blueprint.route("/character/eat", methods=["POST"])
@character_auhtorized
def eat():
    character = g.character

    inventory = Inventory(character.settlement_id, None, character.id)

    if not inventory.has_items('bread', 1):
        return make_response({"error" : "You don't have any bread."}, 400)
    
    inventory.remove_item('bread', 1)

    character.hunger += 6

    if character.hunger <= 24:
        character.health += 1

    elif character.hunger > 28:
        character.health -= 1
    
    db.session.commit()

    socketio.emit("update_character", properties_serializer(character), room=character.settlement_id) # type: ignore

    return make_response({"success" : True}, 204)


@api_blueprint.route("/character/sleep", methods=["POST"])
@character_auhtorized
def sleep():
    character = g.character
    world = World.query.get(character.world_id)
    properties = Properties(character)

    if character.start_sleep:
        if world.current_time > character.end_sleep:
            character.fatigue += math.floor((character.end_sleep - character.start_sleep).total_seconds() / 3600) + 1

        else:
            character.fatigue += math.floor((world.current_time - character.start_sleep).total_seconds() / 3600) - 1

        character.start_sleep = None

    elif not character.end_sleep or (character.end_sleep + timedelta(hours=4) < world.current_time):
        character.start_sleep = world.current_time
        character.end_sleep = world.current_time + timedelta(hours=properties.get_hours_of_sleep(world.current_time.hour))

    else:
        return make_response({"error" : "You just got up, you are not really sleepy."}, 400)
    
    db.session.commit()

    socketio.emit("update_character", properties_serializer(character), room=character.settlement_id) # type: ignore

    return make_response({"success" : True}, 204)


@api_blueprint.route("/character/taxes/pay", methods=["POST"])
@character_auhtorized
def pay_taxes():
    character = g.character

    if character.taxes == 0:
        return make_response({"error" : "You have no taxes to pay"}, 400)
    
    if character.taxes > character.pennies:
        return make_response({"error" : "You don't have enough money to pay your taxes"}, 400)
    
    character.pennies -= character.taxes

    Settlement.query.get(character.settlement_id).taxes += character.taxes

    character.taxes = 0
    
    db.session.commit()

    socketio.emit("update_character", properties_serializer(character), room=character.settlement_id) # type: ignore

    return make_response({"success" : True}, 204)
    

@api_blueprint.route("/world/market", methods=["GET"])
@character_auhtorized
def get_world_market():
    access_key = g.access_key

    market_data = [market_item_serializer(market_item) for market_item in MarketItem.query.filter_by(world_id=access_key.world_id).all()]

    return make_response(market_data, 200)
