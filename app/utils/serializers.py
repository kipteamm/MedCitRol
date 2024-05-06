from app.utils.properties import Properties
from app.teacher.models import Task, TaskField, TaskOption, TaskUser
from app.utils.functions import get_merchandise
from app.utils.tiles import get_tile_index
from app.game.models import World, Settlement, SettlementRuler, Character, Tile, InventoryItem, MarketItem, Merchant
from app.auth.models import User, UserWorlds
from app.extensions import db

import json


def user_serializer(user: User) -> dict:
    return {
        'email' : user.email 
    }


def game_serializer(world: World) -> dict:
    return {
        'id' : world.id,
        'user_id' : world.user_id,
        'code' : world.code,
        'name' : world.name,
        'players' : UserWorlds.query.filter_by(world_id=world.id).count(),
    }


def world_serializer(world: World) -> dict:
    return {
        'id' : world.id,
        'user_id' : world.user_id,
        'code' : world.code,
        'current_time' : world.get_world_time(),
        'settlements' : [small_settlement_serializer(settlement) for settlement in Settlement.query.filter_by(world_id=world.id)],
    }


def settlement_serializer(settlement: Settlement) -> dict:
    return {
        'id' : settlement.id,
        'world_id' : settlement.world_id,
        'name' : settlement.name,
        'colour' : settlement.colour,
        'traderoutes' : json.loads(settlement.traderoutes),
        'hallmark' : settlement.hallmark,
        'citizens' : Character.query.filter_by(settlement_id=settlement.id).count(),
        'revolutionaries' : Character.query.filter_by(settlement_id=settlement.id, revolutionary=True).count(),
        'merchant' : Merchant.query.filter_by(settlement_id=settlement.id).first() is not None,
        'value' : settlement.value_economy,
        'seed' : settlement.seed,
    }


def small_settlement_serializer(settlement: Settlement) -> dict:
    return {
        'id' : settlement.id,
        'name' : settlement.name,
        'colour' : settlement.colour,
        'citizens' : Character.query.filter_by(settlement_id=settlement.id).count(),
    }


def settlement_ruler_serializer(settlement_ruler: SettlementRuler) -> dict:
    return {
        'id' : settlement_ruler.id,
        'settlement_id' : settlement_ruler.settlement_id,
        'name' : settlement_ruler.name,
        'surname' : settlement_ruler.surname,
    }


def character_serializer(character: Character) -> dict:
    properties = Properties(character)

    return {
        'id' : character.id,
        'user_id' : character.user_id,
        'world_id' : character.world_id,
        'settlement_id' : character.settlement_id,
        'hunger' : properties.hunger(),
        'fatigue' : properties.fatigue(),
        'health' : properties.health(),
        'happiness' : properties.happiness(),
        'pennies' : character.pennies,
        'house_id' : character.house_id,
        'profession' : character.profession if character.profession else "unemployed",
        'task_index' : character.task_index,
        'asleep' : character.start_sleep is not None,
        'jailed' : character.jailed,
        'taxes' : character.taxes,
        'revolutionary' : character.revolutionary,
        'inventory' : [inventory_item_serializer(inventory_item) for inventory_item in InventoryItem.query.filter_by(character_id=character.id).all()],
    }


def properties_serializer(character: Character) -> dict:
    properties = Properties(character)

    return {
        'id' : character.id,
        'hunger' : properties.hunger(),
        'fatigue' : properties.fatigue(),
        'health' : properties.health(),
        'happiness' : properties.happiness(),
        'pennies' : character.pennies,
        'profession' : character.profession if character.profession else "unemployed",
        'asleep' : character.start_sleep is not None,
        'jailed' : character.jailed,
        'taxes' : character.taxes,
        'revolutionary' : character.revolutionary,
    }


def tile_serializer(tile: Tile) -> dict:
    character = Character.query.filter_by(id=tile.character_id).first()

    return {
        'id' : tile.id,
        'character_id' : tile.character_id,
        'settlement_id' : tile.settlement_id,
        'name' : character.name if character else None,
        'surname' : character.surname if character else None,
        'pos_x' : tile.pos_x,
        'pos_y' : tile.pos_y,
        'tile_type' : tile.tile_type,
        'tile_index' : get_tile_index(tile.tile_type),
        'future' : tile.future
    }


def inventory_item_serializer(inventory_item: InventoryItem) -> dict:
    return {
        'id' : inventory_item.id,
        'character_id' : inventory_item.character_id,
        'warehouse_id' : inventory_item.warehouse_id,
        'item_type' : inventory_item.item_type,
        'amount' : inventory_item.amount,
        'buildable' : inventory_item.buildable,
        'tile_index' : get_tile_index(inventory_item.item_type)
    }


def market_item_serializer(market_item: MarketItem) -> dict:
    character = Character.query.get(market_item.character_id)

    return {
        'id' : market_item.id,
        'character_id' : market_item.character_id,
        'world_id' : market_item.world_id,
        'settlement_id' : market_item.settlement_id,
        'seller' : f'{character.name} {character.surname}',
        'item_type' : market_item.item_type,
        'amount' : market_item.amount,
        'price' : market_item.price,
    }


def merchant_serializer(merchant: Merchant) -> dict:
    data = {
        "id" : merchant.id,
        "settlement_id" : merchant.settlement_id,
        "end_date" : merchant.end_date,
        "items" : []
    }

    if merchant.merchant_type == "grain":
        for item, price in get_merchandise(merchant.merchant_type).items():
            data["items"].append({
                "id" : item,
                "item_type" : item,
                "amount" : 10000,
                "price" : price
            })

    return data


def task_serializer(task: Task, include_answers: bool=False) -> dict:
    name = TaskField.query.filter_by(task_id=task.id, field_type="header").first()

    if name:
        name = name.content

    else:
        name = "Unnamed"

    finished_users_count = db.session.query(db.func.count(db.func.distinct(TaskUser.user_id))) \
        .filter(TaskUser.task_id == task.id, TaskUser.percentage >= 80) \
        .scalar()
    
    return {
        'id' : task.id,
        'world_id' : task.world_id,
        'index' : task.index,
        'field_index' : task.field_index,
        'name' : name,
        'finished' : finished_users_count,
        'fields' : [task_field_serializer(task_field, include_answers) for task_field in TaskField.query.filter_by(task_id=task.id).order_by(TaskField.field_index)]
    }


def task_field_serializer(task_field: TaskField, include_answers: bool=False) -> dict:
    options = []
    content = task_field.content

    if task_field.field_type == "multiplechoice" or task_field.field_type == "checkboxes" or task_field.field_type == "connect" or task_field.field_type == "order":
        options = [task_option_serializer(task_option, include_answers) for task_option in TaskOption.query.filter_by(task_field_id=task_field.id)]

    elif task_field.field_type == "image":
        content = f'/media/tasks/{content}'

    return { 
        'id' : task_field.id,
        'task_id' : task_field.task_id,
        'field_index' : task_field.field_index,
        'field_type' : task_field.field_type,
        'content' : content,
        'options' : options
    }


def task_option_serializer(task_option: TaskOption, include_answer: bool=False) -> dict:
    data = {
        'id' : task_option.id,
        'task_field_id' : task_option.task_field_id,
        'content' : task_option.content
    }

    if include_answer:
        data['answer'] = task_option.answer
        data['connected'] = task_option.connected

    return data


def task_user_serializer(task_user: TaskUser) -> dict:
    user = User.query.get(task_user.user_id)
    
    return {
        'user_id' : user.id,
        'email' : user.email,
        'percentage' : task_user.percentage,
    }