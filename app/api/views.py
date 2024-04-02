from flask import Blueprint, request, make_response

from app.utils.professions import Profession
from app.utils.inventory import Inventory

from app.teacher.models import Task
from app.game.models import AccessKey, Character, InventoryItem, MarketItem

from app.extensions import db


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

    return make_response(task.get_dict(), 200)


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

    return make_response(task.get_dict(), 200)


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
        Inventory(None, character.id).add_item('farm_land', 9)

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
    
    market_data = [market_item.get_dict() for market_item in MarketItem.query.filter_by(settlement_id=access_key.settlement_id).all()]

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
    
    inventory_item = InventoryItem.query.filter_by(character_id=character.id, item_type=json["item_type"]).first()

    if not inventory_item:
        return make_response({"error" : "Invalid item."}, 400)
    
    if inventory_item.buildable:
        return make_response({"error" : "Invalid item."}, 400)
    
    amount = int(json['amount'])
    price = int(json['price'])
    
    if inventory_item.amount < amount:
        return make_response({"error" : "Invalid amount."}, 400)
    
    inventory_item.amount -= amount

    db.session.commit()

    market_item = MarketItem.query.filter_by(character_id=character.id, settlement_id=access_key.settlement_id, item_type=json["item_type"]).first()

    if not market_item:
        market_item = MarketItem(character_id=character.id, settlement_id=access_key.settlement_id, item_type=json["item_type"])

        db.session.add(market_item)
        db.session.commit()

    market_item.amount += amount
    market_item.price = price

    db.session.commit()

    return make_response(market_item.get_dict(), 200)  
