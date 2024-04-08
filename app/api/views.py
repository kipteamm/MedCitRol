from flask import Blueprint, request, make_response

from app.utils.serializers import market_item_serializer, task_serializer, properties_serializer
from app.utils.professions import Profession
from app.utils.inventory import Inventory
from app.teacher.models import Task
from app.game.models import AccessKey, Character, InventoryItem, MarketItem

from app.extensions import db, socketio


api_blueprint = Blueprint('api', __name__, url_prefix="/api")


@api_blueprint.route("/task", methods=["GET"])
def task():
    authorization = request.headers.get('Authorization')

    access_key = None

    if authorization:
        access_key = AccessKey.query.filter_by(key=authorization).first()

    if not authorization or not access_key:
        return make_response({"error" : "Invalid authentication."}, 401)
    
    character = Character.query.get(access_key.character_id)

    if not character.profession:
        return make_response({"error" : "You have no profession."}, 400)
    
    task = Task.query.filter_by(world_id=access_key.world_id, index=character.task_index).first()
    
    if not task:
        return make_response({"error": "No task found"}, 404)

    return make_response(task_serializer(task), 200)


@api_blueprint.route("/task/submit", methods=["POST"])
def submit_task():
    authorization = request.headers.get('Authorization')

    access_key = None

    if authorization:
        access_key = AccessKey.query.filter_by(key=authorization).first()

    if not authorization or not access_key:
        return make_response({"error" : "Invalid authentication."}, 401)
    
    character = Character.query.get(access_key.character_id)

    if not character.profession:
        return make_response({"error" : "You have no profession."}, 400)
    
    task = Task.query.filter_by(world_id=access_key.world_id, index=character.task_index).first()
    
    if not task:
        return make_response({"error": "No task found"}, 404)
    
    Profession(character).work()

    return make_response(task_serializer(task), 200)


@api_blueprint.route("/profession/set", methods=["PUT"])
def set_profession():
    authorization = request.headers.get('Authorization')

    access_key = None

    if authorization:
        access_key = AccessKey.query.filter_by(key=authorization).first()

    if not authorization or not access_key:
        return make_response({"error" : "Invalid authentication."}, 401)
    
    character = Character.query.get(access_key.character_id)

    json = request.json

    if not json or 'profession' not in json:
        return make_response({"error" : "Invalid profession."}, 400)
    
    profession = json['profession']

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
def get_market():
    authorization = request.headers.get('Authorization')

    access_key = None

    if authorization:
        access_key = AccessKey.query.filter_by(key=authorization).first()

    if not authorization or not access_key:
        return make_response({"error" : "Invalid authentication."}, 401)
    
    market_data = [market_item_serializer(market_item) for market_item in MarketItem.query.filter_by(settlement_id=access_key.settlement_id).all()]

    return make_response(market_data, 200)


@api_blueprint.route("/settlement/market/sell", methods=["POST"])
def sell_item():
    authorization = request.headers.get('Authorization')
        
    access_key = None

    if authorization:
        access_key = AccessKey.query.filter_by(key=authorization).first()

    if not authorization or not access_key:
        return make_response({"error" : "Invalid authentication."}, 401)
    
    character = Character.query.get(access_key.character_id)

    json = request.json

    if not json or not "item_type" in json or not "amount" in json or not "price" in json:
        return make_response({"error" : "Invalid item."}, 400)
    
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
def buy_item():
    authorization = request.headers.get('Authorization')

    access_key = None

    if authorization:
        access_key = AccessKey.query.filter_by(key=authorization).first()

    if not access_key:
        return make_response({"error" : "Invalid authentication."}, 401)
    
    json = request.json

    if not json or not "item_id" in json:
        return make_response({"error" : "Invalid item."}, 400)
    
    character = Character.query.get(access_key.character_id)
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
def eat():
    authorization = request.headers.get('Authorization')

    access_key = None

    if authorization:
        access_key = AccessKey.query.filter_by(key=authorization).first()

    if not access_key:
        return make_response({"error" : "Invalid authentication."}, 401)
    
    character = Character.query.get(access_key.character_id)
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
    