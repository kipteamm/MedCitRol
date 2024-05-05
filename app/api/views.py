from flask import Blueprint, request, make_response, g

from app.utils.serializers import market_item_serializer, task_serializer, properties_serializer, merchant_serializer, task_field_serializer, inventory_item_serializer, settlement_serializer, tile_serializer, character_serializer
from app.utils.decorators import character_auhtorized, authorized
from app.utils.professions import Profession
from app.utils.properties import Properties
from app.utils.inventory import Inventory
from app.utils.functions import get_merchandise
from app.teacher.models import Task, TaskField, TaskOption
from app.game.models import Settlement, Character, MarketItem, World, Merchant, Tile, InventoryItem, Warehouse

from app.extensions import db, socketio

from sqlalchemy import or_

from datetime import timedelta

import random
import string
import math
import os


api_blueprint = Blueprint('api', __name__, url_prefix="/api")


@api_blueprint.route("/build", methods=["PUT"])
@character_auhtorized
def build():
    json = request.json

    if not json:
        return make_response({"error" : "Invalid building."}, 400)
    
    access_key = g.access_key
    
    settlement = Settlement.query.get(access_key.settlement_id)

    if not settlement:
        return make_response({"error": "You cannot build here."}, 400)

    inventory = Inventory(access_key.settlement_id, None, access_key.character_id)

    tiles = []

    for tile in json:
        if not inventory.has_items(tile['tile_type'], 1):
            return make_response({"error": f"You don't have any {tile['tile_type']}."}, 400)

        if Tile.query.filter_by(settlement_id=settlement.id, pos_x=tile['pos_x'], pos_y=tile['pos_y']).first():
            return make_response({"error": f"Something is already built here."}, 400)

        inventory.remove_item(tile['tile_type'], 1)

        tile = Tile(character_id=access_key.character_id, settlement_id=settlement.id, pos_x=tile['pos_x'], pos_y=tile['pos_y'], tile_type=tile['tile_type'])

        db.session.add(tile)
        db.session.commit()

        tiles.append(tile_serializer(tile))
            
    socketio.emit('new_tiles', tiles, room=settlement.id) # type: ignore

    return make_response({'success' : True}, 204)


@api_blueprint.route("/task", methods=["GET"])
@character_auhtorized
def task(): 
    access_key = g.access_key
    character = g.character

    if not character.profession:
        return make_response({"error" : "You have no profession."}, 400)
    
    if character.health < 15:
        return make_response({"error": "You're too ill to work."}, 400)
    
    task = Task.query.filter_by(world_id=access_key.world_id, index=character.task_index).first()
    
    if not task:
        return make_response({"error": "No task found."}, 404)

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
        return make_response({"error": "No task found."}, 404)
    
    json = request.json

    if not json:
        return make_response({"error" : "Invalid answers."}, 400)
    
    correct, wrong = 0, 0
    
    for answer in json:
        task_field = TaskField.query.get(answer['field_id'])

        if not task_field:
            return make_response({"error" : f"no field with id {answer['field_id']} found"}, 400)
        
        if task_field.field_type == "multiplechoice" or task_field.field_type == "checkboxes":
            for _answer in answer['content']:
                if TaskOption.query.filter_by(id=_answer, answer=True).first():
                    correct += 1

                else:
                    wrong += 1

        if task_field.field_type == "connect":
            for connection in answer['content']:
                connection = connection.split("-")

                if TaskOption.query.filter_by(id=connection[0], connected=connection[1]).first():
                    correct += 1

                else:
                    wrong += 1

        if task_field.field_type == "order":
            for i in range(len(answer['content'])):
                if i == 0 and TaskOption.query.filter_by(id=answer['content'][i], connected=None).first():
                    correct += 1

                elif TaskOption.query.filter_by(id=answer['content'][i], connected=last_id).first():
                    correct += 1
                
                else:
                    wrong += 1

                last_id = answer['content'][i]

    percentage = round(correct / (correct + wrong) * 100) 

    if percentage < 80:
        return make_response({"status" : f"You had a bad day at work. You only scored {percentage}% on your task."}, 200)

    elif percentage < 90:
        character.pennies += 2 if character.profession in ['farmer', 'miller', 'baker'] else 4

    else:
        character.pennies += 3 if character.profession in ['farmer', 'miller', 'baker'] else 6  

    character.task_index += 1

    db.session.commit()

    Profession(character).work()

    socketio.emit('update_character', character_serializer(character), room=character.settlement_id) # type: ignore

    return make_response({"status" : f"You scored {percentage}%. Great job!"}, 200)
    


@api_blueprint.route("/profession/set", methods=["PUT"])
@character_auhtorized
def set_profession():
    json = request.json

    if not json or 'profession' not in json:
        return make_response({"error" : "Invalid profession."}, 400)
    
    character = g.character

    if character.profession:
        return make_response({"error" : "You already have a profession."}, 400)

    profession = json['profession']

    character.profession = profession

    if profession == 'farmer':
        Inventory(character.settlement_id, None, character.id).add_item('farm_land', 9)

    elif profession == 'miller':
        Inventory(character.settlement_id, None, character.id).add_item('windmill', 1)

    elif profession == 'baker':
        Inventory(character.settlement_id, None, character.id).add_item('bakery', 1)

    elif profession == 'merchant':
        Inventory(character.settlement_id, None, character.id).add_item('merchant_stall', 1)

    elif profession == 'shoemaker':
        Inventory(character.settlement_id, None, character.id).add_item('shoemaker', 1)
    
    elif profession == 'tanner':
        Inventory(character.settlement_id, None, character.id).add_item('tanner', 1)

    elif profession == 'weaver':
        Inventory(character.settlement_id, None, character.id).add_item('weaver', 1)

    elif profession == 'goldsmith':
        Inventory(character.settlement_id, None, character.id).add_item('goldsmith', 1)

    else:
        return make_response({"error" : "Invalid profession."}, 400)

    socketio.emit("update_character", properties_serializer(character), room=character.settlement_id) # type: ignore
    socketio.emit("alert", {"id" : character.id, "type" : "success", "message" : "Check your build menu!"}, room=character.settlement_id) # type: ignore

    db.session.commit()

    return make_response({"success" : True}, 204)


@api_blueprint.route("/market/<market_type>", methods=["GET"])
@character_auhtorized
def get_settlement_market(market_type):
    if market_type != "settlement" and market_type != "world":
        return make_response({"error" : "Invalid market type."}, 400)
    
    access_key = g.access_key

    if market_type == "settlement":
        market_items = MarketItem.query.filter_by(world_id=None, settlement_id=access_key.settlement_id).all()

    else:
        settlement = Settlement.query.get(access_key.settlement_id)

        market_items = MarketItem.query.filter(
            or_(
                MarketItem.settlement_id.in_(settlement.traderoutes.split(',')),
                MarketItem.settlement_id == settlement.id
            ),
            MarketItem.world_id == access_key.world_id
        ).all()

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
            market_item = MarketItem(character_id=character.id, world_id=access_key.world_id, settlement_id=access_key.settlement_id, item_type=json["item_type"])

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

    if not market_item:
        return make_response({"error" : "Item not found."}, 400)
    
    if market_item.world_id != None:
        settlement = Settlement.query.get(g.access_key.settlement_id)

        if not str(market_item.settlement_id) in settlement.traderoutes.split(','):
            return make_response({"error" : "You can't buy this item."}, 400)
        
    elif market_item.settlement_id != g.access_key.settlement_id:
        return make_response({"error" : "You can't buy this item."}, 400)

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
        character.health += 8

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

    if character.start_sleep:
        hours_slept = (world.current_time - character.start_sleep).total_seconds() / 3600

        if hours_slept > 8:
            character.fatigue += 18

        else:
            character.fatigue += 12 - 8 + hours_slept

        character.start_sleep = None

        if character.health < 18:
            character.health += 6

    elif world.current_time.hour < 20 and world.current_time.hour > 6:
        return make_response({"error" : "You are not really feeling sleepy."}, 400)
    
    else:
        character.start_sleep = world.current_time
    
    db.session.commit()

    socketio.emit("update_character", properties_serializer(character), room=character.settlement_id) # type: ignore

    return make_response({"success" : True}, 204)


@api_blueprint.route("/character/revolution", methods=["POST"])
@character_auhtorized
def revolution():
    character = g.character

    if character.happiness > 10:
        return make_response({"error" : "You are not able to join the revolution."}, 400)
    
    character.revolutionary = not character.revolutionary

    db.session.commit()

    settlement = Settlement.query.get(character.settlement_id)

    settlement.revolution = Character.query.filter_by(settlement_id=character.settlement_id, revolutionary=True).count() > round(Character.query.filter_by(settlement_id=character.settlement_id).count() / 2)
    settlement.start_revolution = World.query.get(settlement.world_id).current_time
    
    db.session.commit()

    socketio.emit("update_character", properties_serializer(character), room=character.settlement_id) # type: ignore
    socketio.emit("update_settlement", settlement_serializer(settlement), room=character.settlement_id) # type: ignore

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


@api_blueprint.route("/character/freedom/request", methods=["POST"])
@character_auhtorized
def request_freedom():
    character = g.character

    if not character.jailed:
        return make_response({"error" : "You are not in jail."}, 400)

    current_time = World.query.get(g.access_key.world_id).current_time

    if character.freedom_request and character.freedom_request + timedelta(hours=2) > current_time:
        return make_response({"error" : "Your ruler starts laughing at you."}, 400)
    
    character.freedom_request = current_time

    db.session.commit()

    if random.randint(1, 4) != 4:
        return make_response({"error" : "Your ruler spits you in the face."}, 400)
    
    character.jailed = False
    character.jail_end = None

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

    task_field = TaskField(task_id=json["task_id"], field_index=task.field_index, field_type=field_type)

    task.field_index += 1

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


@api_blueprint.route('/task/field/move', methods=["PATCH"])
@authorized
def move_field():
    json = request.json

    if not json or not "field_id" in json:
        return make_response({"error" : "invalid json"}, 400)
    
    if not json["direction"] in ["up", "down"]:
        return make_response({"error", "invalid direction"}, 400)
    
    task_field = TaskField.query.get(json["field_id"])

    if json["direction"] == "up":
        if task_field.field_index == 0:
            return make_response({"error" : "cannot be moved up"}, 400)
        
        other_field = TaskField.query.filter_by(task_id=task_field.task_id, field_index=task_field.field_index - 1).first()
    
    if json["direction"] == "down":
        if task_field.field_index == Task.query.get(task_field.task_id).field_index - 1:
            return make_response({"error" : "cannot be moved down"}, 400)
        
        other_field = TaskField.query.filter_by(task_id=task_field.task_id, field_index=task_field.field_index + 1).first()

    if not other_field:
        return make_response({"error" : f"cannot be moved {json['direction']}"}, 400)

    old_index, new_index = task_field.field_index, other_field.field_index

    task_field.field_index = new_index
    other_field.field_index = old_index

    db.session.commit()

    return make_response(task_field_serializer(task_field), 200)


@api_blueprint.route('/task/field/<field_id>/duplicate', methods=["POST"])
@authorized
def duplicate_field(field_id):
    original_task_field = TaskField.query.get(field_id)

    task = Task.query.filter_by(id=original_task_field.task_id, world_id=g.access_key.world_id).first()

    if not task:
        return make_response({"error" : "field not found"}, 400)
    
    task_field = TaskField(task_id=original_task_field.task_id, field_index=task.field_index, field_type=original_task_field.field_type, content=original_task_field.content)

    task.field_index += 1

    db.session.add(task_field)
    db.session.commit()

    if task_field.field_type in ["header", "text", "image"]:
        return make_response(task_field_serializer(task_field), 200)
    
    for original_option in TaskOption.query.filter_by(task_field_id=original_task_field.id).all():
        option = TaskOption(task_field_id=task_field.id, field_type=original_option.field_type, content=original_option.content)

        db.session.add(option)
    
    db.session.commit()

    return make_response(task_field_serializer(task_field), 200)


@api_blueprint.route('/task/field/<field_id>/delete', methods=["DELETE"])
@authorized
def delete_field(field_id):
    task_field = TaskField.query.get(field_id)

    if not task_field:
        return make_response({"error" : "field not found"}, 400)

    task = Task.query.filter_by(id=task_field.task_id, world_id=g.access_key.world_id).first()

    if not task:
        return make_response({"error" : "task not found"}, 400)
    
    for i in range(task.field_index):
        if i <= task_field.field_index:
            continue

        TaskField.query.filter_by(task_id=task_field.task_id, field_index=i).first().field_index -= 1

        db.session.commit()

    if task_field.field_type == "image" and not TaskField.query.filter(TaskField.id != task_field.id, TaskField.content==task_field.content).first():
        path = os.path.join(os.getcwd(), 'media', 'tasks', task_field.content)

        if os.path.exists(path):
            os.remove(path)

    task.field_index -= 1
    
    TaskOption.query.filter_by(task_field_id=field_id).delete()

    db.session.delete(task_field)
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

    task_field = TaskField(task_id=task.id, field_index=task.field_index, field_type="image", content=name)

    task.field_index += 1

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

    if task_field.field_type == "order" and TaskOption.query.filter_by(task_field_id=task_field.id).count() > 0:
        connected_option = TaskOption.query.filter_by(task_field_id=task_field.id, answer=False).first()
        connected_option.answer = True

        task_option.connected = connected_option.id

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

    if not json or not "answers" in json or not "task_id" in json:
        return make_response({"error" : "invalid json"}, 400)

    task = Task.query.get(json["task_id"])

    if not task:
        return make_response({"error" : "No task found."}, 400)
    
    for answer in json['answers']:
        task_field = TaskField.query.get(answer['field_id'])

        if not task_field:
            return make_response({"error" : f"no field with id {answer['field_id']} found"}, 400)
        
        if task_field.field_type == "multiplechoice" or task_field.field_type == "checkboxes":
            for option in TaskOption.query.filter_by(task_field_id=task_field.id).all():
                if option.id in answer['content']:
                    option.answer = True

                else:
                    option.answer = False

            db.session.commit()

        elif task_field.field_type == "connect":
            for connection in answer['content']:
                connection = connection.split("-")

                TaskOption.query.get(int(connection[0])).connected = int(connection[1])
                TaskOption.query.get(int(connection[1])).connected = int(connection[0])

            db.session.commit()

        elif task_field.field_type == "order":
            last_id = None
            
            for i in range(len(answer['content'])):
                option = TaskOption.query.get(answer['content'][i])
                
                if i == 0:
                    option.connected = None

                else:
                    option.connected = last_id

                if i < len(answer['content']) - 1:
                    option.answer = True
                
                else:
                    option.answer = False

                last_id = option.id

            db.session.commit()

    return make_response({"success" : True}, 204)


@api_blueprint.route("/warehouse/<warehouse_id>", methods=["GET"])
@character_auhtorized
def get_warehouse(warehouse_id): 
    access_key = g.access_key

    warehouse = Warehouse.query.filter_by(settlement_id=access_key.settlement_id, tile_id=warehouse_id).first()

    if not warehouse:
        return make_response({"error" : "No warehouse found."}, 400)

    items = []

    for item in InventoryItem.query.filter_by(warehouse_id=warehouse.id).all():
        items.append(inventory_item_serializer(item))

    return make_response(items, 200)
