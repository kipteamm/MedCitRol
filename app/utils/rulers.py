from app.utils.serializers import properties_serializer, tile_serializer
from app.utils.inventory import Inventory
from app.utils.functions import get_coordinates
from app.game.models import Settlement, SettlementRuler, TraderouteRequest, Character, Tile, Warehouse, InventoryItem, MarketItem
from app.extensions import db, socketio

from sqlalchemy import func

from datetime import timedelta, datetime

from typing import Optional, List

from enum import Enum

import random
import json
import math


# 15, 13, 6, 8, 14 -> MORE SOCIAL AND RELIGION

CHARACTERISTICS = ['tyranny', 'economy', 'religion', 'social', 'military']

class Action(Enum):
    SAVE_TAXES = {"characteristics": ["social", "economy"], "price": 0, "previous" : None, "repeatable" : True}
    COLLECT_TAXES = {"characteristics": ["tyranny", "military", "religion", "economy"], "price": 0, "previous" : None, "repeatable" : True}
    EVALUATE_ECONOMY = {"characteristics": ["economy", "social"], "price": 0, "previous" : None, "repeatable" : True}
    CLAIM_LAND = {"characteristics": ["tyranny", "military"], "price": 0, "previous" : None, "repeatable" : False}
    UPGRADE_FORT_1 = {"characteristics": ["tyranny", "military"], "price": 5, "previous" : "CLAIM_LAND", "repeatable" : False}
    UPGRADE_FORT_2 = {"characteristics": ["tyranny", "military"], "price": 15, "previous" : "UPGRADE_FORT_1", "repeatable" : False}
    UPGRADE_FORT_3 = {"characteristics": ["tyranny", "military"], "price": 40, "previous" : "UPGRADE_FORT_2", "repeatable" : False}
    UPGRADE_FORT_4 = {"characteristics": ["tyranny", "military"], "price": 70, "previous" : "UPGRADE_FORT_3", "repeatable" : False}
    UPGRADE_CHURCH_1 = {"characteristics": ["religion", "social"], "price": 5, "previous" : None, "repeatable" : False}
    UPGRADE_CHURCH_2 = {"characteristics": ["religion", "social"], "price": 15, "previous" : "UPGRADE_CHURCH_1", "repeatable" : False}
    UPGRADE_CHURCH_3 = {"characteristics": ["religion", "social"], "price": 40, "previous" : "UPGRADE_CHURCH_2", "repeatable" : False}
    UPGRADE_BOURSE_1 = {"characteristics": ["economy"], "price": 5, "previous" : None, "repeatable" : False}
    UPGRADE_BOURSE_2 = {"characteristics": ["economy"], "price": 15, "previous" : "UPGRADE_BOURSE_1", "repeatable" : False}
    UPGRADE_BOURSE_3 = {"characteristics": ["economy"], "price": 40, "previous" : "UPGRADE_BOURSE_2", "repeatable" : False}
    UPGRADE_BOURSE_4 = {"characteristics": ["economy"], "price": 70, "previous" : "UPGRADE_BOURSE_3", "repeatable" : False}
    UPGRADE_BOURSE_5 = {"characteristics": ["economy"], "price": 120, "previous" : "UPGRADE_BOURSE_4", "repeatable" : False}
    UPGRADE_JAIL_1 = {"characteristics": ["tyranny", "military"], "price": 5, "previous" : None, "repeatable" : False}
    UPGRADE_JAIL_2 = {"characteristics": ["tyranny", "military"], "price": 15, "previous" : "UPGRADE_JAIL_1", "repeatable" : False}
    UPGRADE_JAIL_3 = {"characteristics": ["tyranny", "military"], "price": 40, "previous" : "UPGRADE_JAIL_2", "repeatable" : False}
    UPGRADE_JAIL_4 = {"characteristics": ["tyranny", "military"], "price": 70, "previous" : "UPGRADE_JAIL_3", "repeatable" : False}
    UPGRADE_JAIL_5 = {"characteristics": ["tyranny", "military"], "price": 120, "previous" : "UPGRADE_JAIL_4", "repeatable" : False}
    WAREHOUSE = {"characteristics": ["tyranny", "economy"], "price": 5, "previous" : None, "repeatable" : True}
    STOCK_ITEMS = {"characteristics": ["tyranny", "economy", "religion", "social", "military"], "price" : 1, "previous" : "WAREHOUSE", "repeatable" : True}
    TRADEROUTE = {"characteristics": ["economy"], "price": 0, "previous" : None, "repeatable" : True}
    HALLMARK = {"characteristics": ["tyranny", "military", "religion", "economy", "social"], "price": 0, "previous" : None, "repeatable" : True}
    #FAIR = {"characteristics": ["economy", "social"], "price": 25, "previous" : None, "repeatable" : True}
    #WAR = {"characteristics": ["tyranny", "military"], "price": 100, "previous" : None, "repeatable" : True}

    @property
    def characteristics(self):
        return self.value["characteristics"]

    @property
    def price(self):
        return self.value["price"]
    
    @property
    def previous(self):
        return self.value["previous"]
    
    @property
    def repeatable(self):
        return self.value["repeatable"]

    @property
    def name(self):
        return self._name_


class Ruler:
    def __init__(self, ruler: Optional[SettlementRuler]=None) -> None:
        self._characteristics = {char: 0 for char in CHARACTERISTICS}

        if ruler:
            for char in CHARACTERISTICS:
                self._characteristics[char] = getattr(ruler, char)

            self._ruler = ruler
            self._actions = json.loads(self._ruler.actions)
            self._settlement = Settlement.query.filter_by(id=ruler.settlement_id).first()

    def create(self, settlement_id: int) -> None:
        random.shuffle(CHARACTERISTICS)
        points_left = 250

        for i in range(len(CHARACTERISTICS) - 1):
            random_value = random.randint(5, min(points_left, 100))
            self._characteristics[CHARACTERISTICS[i]] = random_value
            points_left -= random_value

        self._characteristics[CHARACTERISTICS[-1]] = min(points_left, 100)

        with open('app/static/data/names.json') as json_file:
            first_name = random.choice(json.load(json_file))

        with open('app/static/data/surnames.json') as json_file:
            last_name = random.choice(json.load(json_file))

        ruler = SettlementRuler(
            settlement_id=settlement_id,
            name=first_name,
            surname=last_name,
            **self._characteristics
        )

        db.session.add(ruler)
        db.session.commit()

    def evaluate_economy(self) -> int:
        value = self._settlement.taxes
        
        health_sum = Character.query.filter(
            Character.settlement_id == self._settlement.id,
            Character.profession != None
        ).with_entities(func.round(func.sum(100 - Character.health))).scalar() or 0
        value += health_sum

        stored_resources_sum = InventoryItem.query.with_entities(func.sum(InventoryItem.amount)).filter_by(
            settlement_id=self._settlement.id,
            character_id=None
        ).scalar() or 0
        value += stored_resources_sum

        upgrade_fort_values = sum(2 ** i for i in range(4) if f"UPGRADE_FORT_{i + 1}" in self._actions)
        upgrade_church_values = sum(2 ** i for i in range(3) if f"UPGRADE_CHURCH_{i + 2}" in self._actions)
        upgrade_bourse_values = sum(2 ** i for i in range(4) if f"UPGRADE_BOURSE_{i + 2}" in self._actions)
        upgrade_jail_values = sum(2 ** i for i in range(4) if f"UPGRADE_JAIL_{i + 2}" in self._actions)
        value += upgrade_fort_values + upgrade_church_values + upgrade_bourse_values + upgrade_jail_values

        warehouse_count = Tile.query.filter_by(settlement_id=self._settlement.id, tile_type="warehouse").count()
        value += warehouse_count

        self._settlement.value_economy = value

        db.session.commit()

        return value

    def _get_action(self) -> Optional[Action]:
        eligible_actions = []

        for action in Action:
            if action.name in self._actions:
                continue

            if action.name == self._ruler.last_action:
                continue

            if action.price > self._settlement.taxes:
                continue

            if action.previous and not action.previous in self._actions:
                continue

            eligible_actions.append(action)

        if not eligible_actions:
            return None

        total_score_sum = sum(sum(self._characteristics[char] for char in action.characteristics) for action in eligible_actions)
        action_probabilities = {action: sum(self._characteristics[char] for char in action.characteristics) / total_score_sum for action in eligible_actions}

        chosen_action = random.choices(list(action_probabilities.keys()), weights=list(action_probabilities.values()))[0]

        return chosen_action
    
    def _claim_land(self) -> bool:
        coordinates = [
            [0, 0], [1, 0], [2, 0], [3, 0], 
            [0, 1], [1, 1], [2, 1], [3, 1],
            [0, 2], [1, 2], [2, 2], [3, 2],
            [0, 3], [1, 3], [2, 3], [3, 3]
        ]

        pos_x, pos_y = self._random_coordinates(coordinates)

        if not pos_x or not pos_y:
            return False
        
        tiles = []
            
        for i in range(len(coordinates)):
            coordinate = coordinates[i]

            future = "fort" if coordinate != [0, 0] else "fort-0"

            tile = Tile(settlement_id=self._settlement.id, pos_x=pos_x + coordinate[0], pos_y=pos_y + coordinate[1], tile_type="claimed", future=future)

            db.session.add(tile)
            db.session.commit()

            tiles.append(tile_serializer(tile))

        socketio.emit('update_tiles', tiles, room=self._settlement.id) # type: ignore
        socketio.emit('alert', {'type' : 'ruler', 'message' : "Your ruler started building a fort."})

        return True
    
    def _save_taxes(self) -> bool:
        self._settlement.taxes = self._settlement.taxes + math.ceil(self._settlement.taxes * 0.15 * (0 if self._settlement.taxes > 100 else 1)) + (1 if self._settlement.taxes == 0 else 0)

        db.session.commit()

        return True
    
    def _collect_taxes(self, current_time: datetime) -> bool:
        taxes = random.randint(2, 3) if self._characteristics['tyranny'] > self._characteristics['social'] else 2

        for character in Character.query.filter_by(settlement_id=self._settlement.id).all():
            awake = True

            if character.end_sleep and character.end_sleep + timedelta(hours=1) < current_time:
                awake = False

            print(character.taxes > 0, not character.jailed, character.start_sleep == None, awake)

            if character.taxes > 0 and not character.jailed and character.start_sleep == None and awake:
                if "UPGRADE_JAIL_2" in self._actions:
                    character.jailed = True
                    character.jail_end = current_time + timedelta(hours=random.randint(12, 24) if self._characteristics['tyranny'] > self._characteristics['social'] else random.randint(1, 12))
                    character.taxes = 0
                    character.happiness -= max(character.happiness, character.happiness - 6)

                    db.session.commit()

                    continue

            character.taxes = taxes 

            db.session.commit()

            socketio.emit('update_character', properties_serializer(character), room=self._settlement.id) # type: ignore

        socketio.emit('alert', {'type' : 'ruler', 'message' : "Your ruler requested {taxes} penningen in taxes."})

        return True
    
    def _upgrade_fort(self, level: str) -> bool:
        random_value = random.randint(0, 1)

        tile_changes = {
            "UPGRADE_FORT_1": [(1, 1, "small_fort")],
            "UPGRADE_FORT_2": [(1, 2, f"fort_top_left_{random_value}"), (2, 2, f"fort_top_right_{random_value}"), (3, 1, f"fort_bottom_left_{random_value}"), (2, 1, f"fort_bottom_right_{random_value}")],
            "UPGRADE_FORT_3": [(0, 0, f"tower_right_{random_value}"), (3, 0, f"tower_left_{random_value}"), (0, 3, f"tower_right_{random_value}"), (3, 3, f"tower_left_{random_value}")],
            "UPGRADE_FORT_4": [(0, 1, "wall_vertical"), (0, 2, "wall_vertical"), (1, 0, "wall_horizontal"), (2, 0, "wall_horizontal"), (3, 1, "wall_vertical"), (3, 2, "wall_vertical"), (1, 3, "wall_horizontal"), (2, 3, "wall_horizontal")]
        }
        
        changes = tile_changes.get(level)

        tiles = []

        if not changes:
            return False
        
        corner = Tile.query.filter_by(settlement_id=self._settlement.id, future="fort-0").first()

        if not corner:
            return False

        pos_x, pos_y = corner.pos_x, corner.pos_y
        
        for x, y, tile_type in changes:
            tile = Tile.query.filter_by(settlement_id=self._settlement.id, pos_x=pos_x + x, pos_y=pos_y + y).first()
                
            tile.tile_type = tile_type

            tiles.append(tile_serializer(tile))

        db.session.commit()

        socketio.emit('update_tiles', tiles, room=self._settlement.id) # type: ignore
        socketio.emit('alert', {'type' : 'ruler', 'message' : "Your ruler upgraded his fort."})

        return True

    def _random_coordinates(self, tiles: list, well: bool=False) -> tuple[Optional[int], Optional[int]]:
        house_count = Tile.query.filter_by(settlement_id=self._settlement.id, tile_type="hut").count()

        house = Tile.query.filter_by(settlement_id=self._settlement.id, tile_type="hut").offset(random.randint(0, house_count - 1)).first()

        if not house:
            print("no random house")

            return None, None

        while True:
            pos_x = random.randint(abs(house.pos_x - 10), 47)
            pos_y = random.randint(27, 47)

            for tile in tiles:
                _tile = Tile.query.filter_by(settlement_id=self._settlement.id, pos_x=pos_x + tile[0], pos_y=pos_y + tile[1]).first()

                if _tile:
                    if not well or (well and _tile.tile_type != "well"):
                        return None, None
                
            break

        return pos_x, pos_y

    def _upgrade_church(self, level: str) -> bool:
        tiles = []

        if level == "UPGRADE_CHURCH_1":
            pos_x, pos_y = self._random_coordinates([[0, 0], [1, 0]])

            if not pos_x or not pos_y:
                return False

            tile_1 = Tile(settlement_id=self._settlement.id, pos_x=pos_x, pos_y=pos_y, tile_type="claimed", future="church_chapel")

            db.session.add(tile_1)

            tile_2 = Tile(settlement_id=self._settlement.id, pos_x=pos_x + 1, pos_y=pos_y, tile_type="claimed", future="church_tower")

            db.session.add(tile_2)

            db.session.commit()

            tiles.append(tile_serializer(tile_1))
            tiles.append(tile_serializer(tile_2))

            socketio.emit('alert', {'type' : 'ruler', 'message' : "Your ruler started building a church."})

        if level == "UPGRADE_CHURCH_2":
            tile = Tile.query.filter_by(settlement_id=self._settlement.id, future="church_chapel").first()
            
            tile.tile_type = "church_chapel"

            tiles.append(tile_serializer(tile))

            socketio.emit('alert', {'type' : 'ruler', 'message' : "Your ruler continued constructing the church."})

        if level == "UPGRADE_CHURCH_3":
            tile = Tile.query.filter_by(settlement_id=self._settlement.id, future="church_tower").first()
            
            tile.tile_type = "church_tower"

            tiles.append(tile_serializer(tile))

            socketio.emit('alert', {'type' : 'ruler', 'message' : "Your ruler finished constructing the church."})

        db.session.commit()
        
        socketio.emit('update_tiles', tiles, room=self._settlement.id) # type: ignore

        return True
    
    def _upgrade_bourse(self, level: str) -> bool:
        tiles = []

        if level == "UPGRADE_BOURSE_1":
            coordinates = [[0, 0], [1, 0], [0, 1], [1, 1]]

            pos_x, pos_y = self._random_coordinates(coordinates)

            if not pos_x or not pos_y:
                return False
            
            for i in range(len(coordinates)):
                coordinate = coordinates[i]

                tile = Tile(settlement_id=self._settlement.id, pos_x=pos_x + coordinate[0], pos_y=pos_y + coordinate[1], tile_type="claimed", future=f"bourse_{i}")

                db.session.add(tile)
                db.session.commit()

                tiles.append(tile_serializer(tile))

            socketio.emit('alert', {'type' : 'ruler', 'message' : "Your ruler started building a bourse."})

        else:
            tile_type_mapping = {
                "UPGRADE_BOURSE_2": "bourse_0",
                "UPGRADE_BOURSE_3": "bourse_1",
                "UPGRADE_BOURSE_4": "bourse_2",
                "UPGRADE_BOURSE_5": "bourse_3"
            }
            
            tile_type = tile_type_mapping.get(level)

            tile = Tile.query.filter_by(settlement_id=self._settlement.id, tile_type="claimed", future=tile_type).first()

            tile.tile_type = tile_type

            tiles.append(tile_serializer(tile))

            socketio.emit('alert', {'type' : 'ruler', 'message' : "Your ruler continued constructing the bourse."})

        db.session.commit()

        socketio.emit('update_tiles', tiles, room=self._settlement.id) # type: ignore

        return True
    
    def _upgrade_jail(self, level: str) -> bool:
        tiles = []

        if level == "UPGRADE_JAIL_1":
            coordinates = [[0, 0], [1, 0], [0, 1], [1, 1]]

            pos_x, pos_y = self._random_coordinates(coordinates)

            if not pos_x or not pos_y:
                return False
            
            for i in range(len(coordinates)):
                coordinate = coordinates[i]

                tile = Tile(settlement_id=self._settlement.id, pos_x=pos_x + coordinate[0], pos_y=pos_y + coordinate[1], tile_type="claimed", future=f"jail_{i}")

                db.session.add(tile)
                db.session.commit()

                tiles.append(tile_serializer(tile))

            socketio.emit('alert', {'type' : 'ruler', 'message' : "Your ruler started building a jail."})

        else:
            tile_type_mapping = {
                "UPGRADE_JAIL_2": "jail_0",
                "UPGRADE_JAIL_3": "jail_1",
                "UPGRADE_JAIL_4": "jail_2",
                "UPGRADE_JAIL_5": "jail_3"
            }
            
            tile_type = tile_type_mapping.get(level)

            tile = Tile.query.filter_by(settlement_id=self._settlement.id, tile_type="claimed", future=tile_type).first()

            tile.tile_type = tile_type

            tiles.append(tile_serializer(tile))

            socketio.emit('alert', {'type' : 'ruler', 'message' : "Your ruler continued constructing the jail."})

        db.session.commit()

        socketio.emit('update_tiles', tiles, room=self._settlement.id) # type: ignore

        return True

    def _warehouse(self) -> bool:
        pos_x, pos_y = self._random_coordinates([[0, 0]])

        if not pos_x or not pos_y:
            return False
        
        tile = Tile(settlement_id=self._settlement.id, pos_x=pos_x, pos_y=pos_y, tile_type="warehouse")

        db.session.add(tile)
        db.session.commit()

        warehouse = Warehouse(settlement_id=self._settlement.id, tile_id=tile.id)

        db.session.add(warehouse)
        db.session.commit()

        socketio.emit('update_tiles', [tile_serializer(tile)], room=self._settlement.id) # type: ignore

        socketio.emit('alert', {'type' : 'ruler', 'message' : "Your ruler built a warehouse."})

        return True
    
    def _stock_items(self) -> bool:
        warehouse = Warehouse.query.filter_by(settlement_id=self._settlement.id).filter(Warehouse.capacity < 100).first()

        if not warehouse:
            print("no warehouse")

            return False

        available_items = MarketItem.query.filter_by(settlement_id=self._settlement.id).filter(MarketItem.price <= self._settlement.taxes).all()

        if not available_items:
            print("no available items")

            return False

        stored_items = {item.item_type: item.amount for item in InventoryItem.query.filter_by(settlement_id=self._settlement.id, character_id=None).all()}

        sorted_items = sorted(available_items, key=lambda item: stored_items.get(item.item_type, 0))
        random_item = sorted_items[0] if sorted_items else None

        if not random_item:
            print("no random item")

            return False
        
        max_amount = min(random_item.amount, math.floor(self._settlement.taxes / random_item.price))
        amount = max(1, random.randint(1, max_amount))

        random_item.amount -= amount

        if random_item.amount == 0:
            db.session.delete(random_item)
            db.session.commit()

        Inventory(self._settlement.id, warehouse.id, None).add_item(random_item.item_type, amount)

        character = Character.query.get(random_item.character_id)
        character.pennies += amount * random_item.price
        
        db.session.commit()

        socketio.emit("update_character", properties_serializer(character), room=self._settlement.id) # type: ignore
        socketio.emit('alert', {'type' : 'ruler', 'message' : "Your ruler stored items in a warehouse."})

        return True
    
    def _manage_traderoute_requests(self, traderoute_requests: List[TraderouteRequest]) -> bool:
        social = (self._characteristics['social'] + self._characteristics['religion'] + self._characteristics['military']) / 3

        traderoute = None

        if self._characteristics['tyranny'] > social or self._characteristics['economy'] > social:
            traderoute = traderoute_requests.order_by(TraderouteRequest.taxes.desc()).first() # type: ignore

        else:
            traderoute = traderoute_requests.order_by("?").first() # type: ignore

        if not traderoute:
            return False
        
        Settlement.query.get(traderoute.settlement).traderoutes += f",{traderoute.traderoute}"
        Settlement.query.get(traderoute.traderoute).traderoutes += f",{self._settlement.id}"

        db.session.delete(traderoute)
        db.session.commit()

        socketio.emit('alert', {'type' : 'ruler', 'message' : "Your ruler accepted a traderoute request."})

        return True
    
    def _traderoute(self) -> bool:
        traderoute_requests = TraderouteRequest.query.filter_by(traderoute_id=self._settlement.id).all()

        if traderoute_requests:
            return self._manage_traderoute_requests(traderoute_requests)

        traderoute_settlement_ids = self._settlement.traderoutes.split(",")

        new_traderoutes = Settlement.query.filter(
            Settlement.id!= self._settlement.id,
            Settlement.id not in traderoute_settlement_ids
        ).all()

        if not new_traderoutes:
            new_traderoutes = [traderoute for traderoute in ["Antwerp", "Brugge", "Gent"] if traderoute not in traderoute_settlement_ids]

            if not new_traderoutes:
                return False
            
            self._settlement.traderoutes += f'{"" if len(traderoute_settlement_ids) == 0 else ","}{random.choice(new_traderoutes)}'

            db.session.commit()

            return True
        
        closest_traderoute = min(new_traderoutes, key=lambda t: abs(t.taxes - self._settlement.taxes))

        if not closest_traderoute:
            return False

        traderoute_request = TraderouteRequest(settlement_id=self._settlement.id, traderoute_id=closest_traderoute.id)

        db.session.add(traderoute_request)

        socketio.emit('alert', {'type' : 'ruler', 'message' : "Your ruler requested a traderoute with another settlement."})

        return True
    
    def _hallmark(self) -> bool:
        if self._settlement.value_economy < 100:
            return False
        
        not_military = (self._characteristics['tyranny'] + self._characteristics['economy'] + self._characteristics['social'] + self._characteristics['religion']) / 4

        if self._characteristics['military'] > not_military:
            self._settlement.hallmark = True
            self._actions.append("HALLMARK")
            self._ruler.actions = json.dumps(self._actions)

            socketio.emit('alert', {'type' : 'ruler', 'message' : "Your city is now approved by your king."})

            return True
        
        if random.randint(1, 4) < 4:
            return False
        
        self._settlement.hallmark = True
        self._actions.append("HALLMARK")
        self._ruler.actions = json.dumps(self._actions)

        db.session.commit()

        socketio.emit('alert', {'type' : 'ruler', 'message' : "Your city is now approved by your king."})

        return True

    def work(self, current_time: datetime) -> None:
        if random.randint(1, 4) != 2:
            print(f"not doing anything")

            return None
        
        if self._ruler.last_action_date and self._ruler.last_action_date + timedelta(days=1) < current_time:
            print("inactivity taxes save")

            self._save_taxes()

        action = self._get_action()

        if not action:
            print("no action")

            return
        
        print(f"{self._ruler.name} {self._ruler.surname} started working on {action.name}")
        
        success = False
        
        if action == Action.SAVE_TAXES:
            success = self._save_taxes()
        
        if action == Action.COLLECT_TAXES:
            success = self._collect_taxes(current_time)

        if action == Action.EVALUATE_ECONOMY:
            self.evaluate_economy()

            success = True

        if action == Action.CLAIM_LAND:
            success = self._claim_land()
        
        if "UPGRADE_FORT_" in action.name:
            success = self._upgrade_fort(action.name)
        
        if "UPGRADE_CHURCH_" in action.name:
            success = self._upgrade_church(action.name)

        if "UPGRADE_BOURSE_" in action.name:
            success = self._upgrade_bourse(action.name)

        if "UPGRADE_JAIL_" in action.name:
            success = self._upgrade_jail(action.name)

        if action == Action.WAREHOUSE:
            success = self._warehouse()

        if action == Action.STOCK_ITEMS:
            success = self._stock_items()

        if action == Action.TRADEROUTE:
            success = self._traderoute()

        if action == Action.HALLMARK:
            success = self._hallmark()

        if not success:
            print(f"no success on {action.name}")

            return

        if not action.repeatable or (action.name == "WAREHOUSE" and Tile.query.filter_by(settlement_id=self._settlement.id, tile_type="warehouse").count() >= 4):
            self._actions.append(action.name)
            self._ruler.actions = json.dumps(self._actions)

            db.session.commit()

        self._settlement.taxes -= action.price

        print(self._ruler.last_action_date, current_time)

        self._ruler.last_action_date = current_time
        self._ruler.last_action = action.name

        db.session.commit()

        print(f"{self._ruler.name} {self._ruler.surname} finished {action.name} for {action.price}")
