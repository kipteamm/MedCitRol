from app.teacher.models import Task, TaskField, TaskOption
from app.utils.properties import Properties
from app.utils.tiles import get_tile_index
from app.game.models import World, Settlement, Character, Tile, InventoryItem, MarketItem

def world_serializer(world: World) -> dict:
    return {
        'id' : world.id,
        'user_id' : world.id,
        'code' : world.code,
        'current_time' : world.get_world_time()
    }


def settlement_serializer(settlement: Settlement) -> dict:
    return {
        'id' : settlement.id,
        'world_id' : settlement.world_id,
        'name' : settlement.name,
        'colour' : settlement.colour,
        'inventory' : [inventory_item_serializer(inventory_item) for inventory_item in InventoryItem.query.filter_by(settlement_id=settlement.id).all()]
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
        'profession' : character.profession,
        'task_index' : character.task_index,
        'asleep' : character.start_sleep is not None,
        'inventory' : [inventory_item_serializer(inventory_item) for inventory_item in InventoryItem.query.filter_by(character_id=character.id).all()]
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
        'profession' : character.profession,
        'asleep' : character.start_sleep is not None,
    }


def tile_serializer(tile: Tile) -> dict:
    return {
        'id' : tile.id,
        'character_id' : tile.character_id,
        'settlement_id' : tile.settlement_id,
        'pos_x' : tile.pos_x,
        'pos_y' : tile.pos_y,
        'tile_type' : tile.tile_type,
        'tile_index' : get_tile_index(tile.tile_type),
    }


def inventory_item_serializer(inventory_item: InventoryItem) -> dict:
    return {
        'id' : inventory_item.id,
        'character_id' : inventory_item.character_id,
        'settlement_id' : inventory_item.settlement_id,
        'item_type' : inventory_item.item_type,
        'amount' : inventory_item.amount,
        'buildable' : inventory_item.buildable,
        'tile_index' : get_tile_index(inventory_item.item_type)
    }


def market_item_serializer(market_item: MarketItem) -> dict:
    return {
        'id' : market_item.id,
        'character_id' : market_item.character_id,
        'world_id' : market_item.world_id,
        'settlement_id' : market_item.settlement_id,
        'item_type' : market_item.item_type,
        'amount' : market_item.amount,
        'price' : market_item.price,
    }


def task_serializer(task: Task) -> dict:
    return {
        'id' : task.id,
        'world_id' : task.world_id,
        'index' : task.index,
        'fields' : [task_field_serializer(task_field) for task_field in TaskField.query.filter_by(task_id=task.id)]
    }


def task_field_serializer(task_field: TaskField) -> dict:
    options = []

    if task_field.field_type == "multiplechoice" or task_field.field_type == "checkboxes" or task_field.field_type == "connect" or task_field.type == "order":
        options = [task_option_serializer(task_option) for task_option in TaskOption.query.filter_by(task_field_id=task_field.id)]

    return { 
        'id' : task_field.id,
        'task_id' : task_field.task_id,
        'field_type' : task_field.field_type,
        'content' : task_field.content,
        'options' : options
    }


def task_option_serializer(task_option: TaskOption) -> dict:
    return {
        'id' : task_option.id,
        'task_field_id' : task_option.task_field_id,
        'content' : task_option.content
    }
