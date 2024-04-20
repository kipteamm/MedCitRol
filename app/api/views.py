from flask import Blueprint, request, make_response, g

from app.utils.serializers import market_item_serializer, task_serializer, properties_serializer, merchant_serializer, task_field_serializer
from app.utils.decorators import character_auhtorized, authorized
from app.utils.properties import Properties
from app.utils.inventory import Inventory
from app.utils.functions import get_merchandise
from app.teacher.models import Task, TaskField, TaskOption
from app.game.models import Settlement, Character, MarketItem, World, Merchant, Tile

from app.extensions import db, socketio

from datetime import timedelta

import random
import string
import math
import os


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
    
    json = request.json

    if not json:
        return make_response({"error" : "Invalid answers."}, 400)

    return make_response({"success" : True}, 204)


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


@api_blueprint.route("/market/<market_type>", methods=["GET"])
@character_auhtorized
def get_settlement_market(market_type):
    if market_type != "settlement" and market_type != "world":
        return make_response({"error" : "Invalid market type."}, 400)
    
    access_key = g.access_key

    if market_type == "settlement":
        market_items = MarketItem.query.filter_by(settlement_id=access_key.settlement_id).all()

    else:
        market_items = MarketItem.query.filter_by(world_id=access_key.world_id).all()

    market_data = [market_item_serializer(market_item) for market_item in market_items]

    return make_response(market_data, 200)


@api_blueprint.route("/market/<market_type>/sell", methods=["POST"])
@character_auhtorized
def sell_item(market_type):
    if market_type != "settlement" and market_type != "world":
        return make_response({"error" : "Invalid market type."}, 400)

    json = request.json

    if not json or not "item_type" in json or not "amount" in json or not "price" in json:
        return make_response({"error" : "Invalid item."}, 400)
    
    access_key = g.access_key
    character = g.character

    if market_type == "world" and not Tile.query.filter_by(settlement_id=character.settlement_id, character_id=character.id, tile_type="market_stall").first():
        return make_response({"error", "You don't own a market stall."})
    
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

    if market_type == "settlement":
        market_item = MarketItem.query.filter_by(character_id=character.id, settlement_id=access_key.settlement_id, item_type=json["item_type"]).first()

    else:
        market_item = MarketItem.query.filter_by(character_id=character.id, world_id=access_key.world_id, item_type=json["item_type"]).first()

    if not market_item:
        if market_type == "settlement":
            market_item = MarketItem(character_id=character.id, settlement_id=access_key.settlement_id, item_type=json["item_type"])
        
        else:
            market_item = MarketItem(character_id=character.id, world_id=access_key.world_id, item_type=json["item_type"])

        db.session.add(market_item)
        db.session.commit()

    market_item.amount += amount
    market_item.price = price

    db.session.commit()

    return make_response(market_item_serializer(market_item), 200)  


@api_blueprint.route("/market/<market_type>/buy", methods=["POST"])
@character_auhtorized
def buy_item(market_type):
    if market_type != "settlement" and market_type != "world":
        return make_response({"error" : "Invalid market type."}, 400)
    
    json = request.json

    if not json or not "item_id" in json:
        return make_response({"error" : "Invalid item."}, 400)
    
    character = g.character
    
    market_item = MarketItem.query.get(json["item_id"])

    if character.pennies < market_item.price:
        return make_response({"error" : "You don't have enough money."}, 400)
    
    market_item.amount -= 1
    character.pennies -= market_item.price

    seller = Character.query.get(market_item.character_id)
    seller.pennies += market_item.price
    
    Inventory(character.settlement_id, None, character.id).add_item(market_item.item_type, 1)

    db.session.commit()

    if market_item.amount == 0:
        db.session.delete(market_item)
        db.session.commit()

    socketio.emit("update_character", properties_serializer(seller), room=seller.settlement_id) # type: ignore

    return make_response({"success" : True}, 204)


@api_blueprint.route("/character/eat", methods=["POST"])
@character_auhtorized
def eat():
    character = g.character

    inventory = Inventory(character.settlement_id, None, character.id)

    if not inventory.has_items('bread', 1):
        return make_response({"error" : "You don't have any food."}, 400)
    
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

    elif not character.end_sleep or (character.end_sleep + timedelta(hours=2) < world.current_time):
        character.start_sleep = world.current_time
        character.end_sleep = world.current_time + timedelta(hours=properties.get_hours_of_sleep(world.current_time.hour))

    else:
        print(character.end_sleep + timedelta(hours=2), world.current_time)

        return make_response({"error" : "You just got up, you are not feeling sleepy."}, 400)
    
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


@api_blueprint.route("/merchant", methods=["GET"])
@character_auhtorized
def get_merchant_market():
    access_key = g.access_key

    merchant = Merchant.query.filter_by(settlement_id=access_key.settlement_id).first()

    if not merchant:
        return make_response({"error" : "No merchant is currently in town."}, 400)

    market_data = merchant_serializer(merchant)


    return make_response(market_data, 200)


@api_blueprint.route("/merchant/buy", methods=["POST"])
@character_auhtorized
def merchant_buy_item():
    json = request.json

    if not json or not "item_id" in json:
        return make_response({"error" : "Invalid item."}, 400)
    
    merchant = Merchant.query.filter_by(settlement_id=g.access_key.settlement_id).first()

    if not merchant:
        return make_response({"error" : "No merchant is currently in town."}, 400)
    
    merchandise = get_merchandise(merchant.merchant_type)

    item = json['item_id']

    if not item in merchandise:
        return make_response({"error" : "Invalid item."}, 400)
    
    character = g.character

    if character.pennies < merchandise[item]:
        return make_response({"error" : "You don't have enough money."}, 400)
    
    character.pennies -= merchandise[item]
    
    Inventory(character.settlement_id, None, character.id).add_item(item, 1)

    db.session.commit()

    socketio.emit("update_character", properties_serializer(character), room=character.settlement_id) # type: ignore

    return make_response({"success" : True}, 204)


@api_blueprint.route("/buildable/purchase", methods=["POST"])
@character_auhtorized
def purchase_buildable():
    json = request.json

    if not json or not "item_type" in json:
        return make_response({"error" : "Invalid item."}, 400)
    
    merchandise = get_merchandise("buildable")

    item = json['item_type']

    if not item in merchandise:
        return make_response({"error" : "Invalid item."}, 400)
    
    character = g.character

    if character.pennies < merchandise[item]:
        return make_response({"error" : "You don't have enough money."}, 400)
    
    character.pennies -= merchandise[item]
    
    Inventory(character.settlement_id, None, character.id).add_item(item, 1)

    db.session.commit()

    socketio.emit("update_character", properties_serializer(character), room=character.settlement_id) # type: ignore

    return make_response({"success" : True}, 204)


@api_blueprint.route('/task/field/add', methods=["POST"])
@authorized
def add_field():
    json = request.json

    if not json or not "field_type" in json or not "task_id" in json:
        return make_response({"error" : "invalid json"}, 400)
    
    task = Task.query.get(json["task_id"])

    field_type = json["field_type"]

    if not field_type in ["header", "text", "image", "multiplechoice", "checkboxes", "connect", "order"]:
        return make_response({"error" : "invalid field type"}, 400)

    task_field = TaskField(task_id=json["task_id"], field_type=field_type)

    db.session.add(task_field)
    db.session.commit()

    return make_response(task_field_serializer(task_field), 200)


@api_blueprint.route('/task/field/edit', methods=["PATCH"])
@authorized
def edit_field():
    json = request.json

    if not json or not "field_id" in json:
        return make_response({"error" : "invalid json"}, 400)
    
    task_field = TaskField.query.get(json["field_id"])

    if task_field.field_type in ["header", "text"] and not "content" in json:
        return make_response({"error", "missing content"})

    task_field.content = json["content"] if json["content"] else None

    db.session.commit()

    return make_response(task_field_serializer(task_field), 200)


@api_blueprint.route('/task/image/add', methods=["POST"])
@authorized
def upload_file():
    if 'image' not in request.files:
        return make_response({"error" : "no image 1"}, 400)

    file = request.files['image']

    if not file.filename:
        return make_response({"error" : "no image 2"}, 400)

    task = Task.query.get(request.form.get('task_id'))

    while True:
        name = f"{''.join(random.choices(string.ascii_letters, k=16))}.{file.filename.split('.')[1]}"

        if not TaskField.query.filter_by(field_type="image", content=name).first():
            break

    task_field = TaskField(task_id=task.id, field_type="image", content=name)

    db.session.add(task_field)
    db.session.commit()

    tasks_dir = os.path.join(os.getcwd(), 'media', 'tasks')

    os.makedirs(tasks_dir, exist_ok=True)

    file_path = os.path.join(tasks_dir, name)
    file.save(file_path)

    return make_response(task_field_serializer(task_field), 200)


@api_blueprint.route('/task/option/add', methods=["POST"])
@authorized
def add_option():
    json = request.json

    if not json or not "field_id" in json:
        return make_response({"error" : "invalid json"}, 400)
    
    task_field = TaskField.query.get(json["field_id"])

    if task_field.field_type not in ["multiplechoice", "checkboxes", "connect", "order"]:
        return make_response({"error", "you cannot add an option to this field"}, 400)

    if TaskOption.query.filter_by(task_field_id=json["field_id"], content=None).first():
        return make_response({"error" : "already have an empty option"}, 400)
    
    if TaskOption.query.filter_by(task_field_id=json["field_id"]).count() >= 26:
        return make_response({"error" : "you maxed out the amoutn of options"}, 400)

    task_option = TaskOption(task_field_id=json["field_id"])

    db.session.add(task_option)
    db.session.commit()

    return make_response(task_field_serializer(task_field), 200)


@api_blueprint.route('/task/option/edit', methods=["PATCH"])
@authorized
def edit_option():
    json = request.json

    if not json or not "option_id" in json or not "content" in json:
        return make_response({"error" : "invalid json"}, 400)
    
    task_option = TaskOption.query.get(json["option_id"])
    content = json["content"]

    if TaskOption.query.filter_by(task_field_id=task_option.task_field_id, content=content).first():
        return make_response({"error" : "you already have this option"}, 400)

    task_option.content = content

    db.session.commit()

    return make_response(task_field_serializer(TaskField.query.get(task_option.task_field_id)), 200)


@api_blueprint.route('/task/answers', methods=["PATCH"])
@authorized
def update_answers():
    json = request.json

    print(json)

    if not json or not "answers" in json or not "task_id" in json:
        return make_response({"error" : "invalid json"}, 400)

    task = Task.query.get(json["task_id"])

    if not task:
        return make_response({"error" : "no task found"}, 400)
    
    for answer in json.answers:
        task_field = TaskField.query.get(['field_id'])

        if not task_field:
            return make_response({"error", f"no field with id {answer['field_id']} found"})
        
        if task_field.field_type == "multiplechoice" or task_field.field_type == "checkboxes":
            update_query = (
                TaskOption.__table__
                .update()
                .where(TaskOption.id.in_(answer['content']))
                .values(answer=True)
            )

            db.session.execute(update_query)
            db.session.commit()

    return make_response({"success" : True}, 204)