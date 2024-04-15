from app.utils.serializers import properties_serializer, tile_serializer
from app.utils.functions import get_coordinates
from app.game.models import Settlement, SettlementRuler, Character, Tile, Warehouse
from app.extensions import db, socketio

from datetime import timedelta, datetime

from typing import Optional

from enum import Enum

import random
import json
import math


# 13, 12, 4, 7, 12 -> MORE SOCIAL AND RELIGION

CHARACTERISTICS = ['tyranny', 'economy', 'religion', 'social', 'military', 'carelessness']


class Action(Enum):
    CLAIM_LAND = {"characteristics": ["tyranny", "military"], "price": 0, "previous" : None, "repeatable" : False}
    SAVE_TAXES = {"characteristics": ["social", "economy"], "price": 0, "previous" : None, "repeatable" : True}
    COLLECT_TAXES = {"characteristics": ["tyranny", "military", "religion", "economy"], "price": 0, "previous" : None, "repeatable" : True}
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
    WAREHOUSE = {"characteristics": ["tyranny", "economy"], "price": 10, "previous" : None, "repeatable" : True}
    #STOCK_ITEMS = {"characteristics": ["tyranny", "economy", "social"], "price" : 1, "previous" : "WAREHOUSE", "repeatable" : True}
    #TRADEROUTE = {"characteristics": ["economy"], "price": 0, "previous" : None, "repeatable" : True}
    #HALLMARK = {"characteristics": ["tyranny", "economy", "social"], "price": 0, "previous" : None, "repeatable" : True}
    #WAR = {"characteristics": ["tyranny", "military"], "price": 100, "previous" : None, "repeatable" : True}
    #FAIR = {"characteristics": ["economy", "social"], "price": 25, "previous" : None, "repeatable" : True}

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
        points_left = 300

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

    def _get_action(self) -> Optional[Action]:
        eligible_actions = []

        for action in Action:
            if action.name in self._actions:
                continue

            if action == Action.SAVE_TAXES and random.randint(0, 1) == 0:
                continue

            if action.price > self._settlement.taxes:
                continue

            if action.previous and not action.previous in self._actions:
                continue

            if action.name == "WAREHOUSE" and Tile.query.filter_by(settlement_id=self._settlement.id, tile_type="warehouse").count() >= 4:
                continue

            eligible_actions.append(action)

        if not eligible_actions:
            return None

        total_score_sum = sum(sum(self._characteristics[char] for char in action.characteristics) for action in eligible_actions)
        action_probabilities = {action: sum(self._characteristics[char] for char in action.characteristics) / total_score_sum for action in eligible_actions}

        chosen_action = random.choices(list(action_probabilities.keys()), weights=list(action_probabilities.values()))[0]

        return chosen_action
    
    def _claim_land(self) -> bool:
        coordinates = get_coordinates(37, 37, 1)
        coordinates.extend(get_coordinates(37, 37, 2))

        tiles = []

        for coordinate in coordinates:
            if Tile.query.filter_by(settlement_id=self._settlement.id, pos_x=coordinate[0], pos_y=coordinate[1]).first():
                continue

            tile = Tile(pos_x=coordinate[0], pos_y=coordinate[1], settlement_id=self._settlement.id, tile_type="claimed", future="fort")

            db.session.add(tile)

            tiles.append(tile_serializer(tile))

        db.session.commit()

        socketio.emit('update_tiles', tiles, room=self._settlement.id) # type: ignore

        return True
    
    def _save_taxes(self) -> bool:
        self._settlement.taxes = self._settlement.taxes + math.ceil(self._settlement.taxes * 0.15 * (0 if self._settlement.taxes > 100 else 1)) + (1 if self._settlement.taxes == 0 else 0)

        db.session.commit()

        return True
    
    def _collect_taxes(self, current_time: datetime) -> bool:
        for character in Character.query.filter_by(settlement_id=self._settlement.id).all():
            if character.taxes > 0:
                if "UPGRADE_JAIL_2" in self._actions:
                    character.jailed = True
                    character.jail_end = current_time + timedelta(hours=random.randint(12, 24) if self._characteristics['tyranny'] > self._characteristics['social'] else random.randint(1, 12))
                    character.taxes = 0

            else:
                character.taxes = random.randint(2, 3) if self._characteristics['tyranny'] > self._characteristics['social'] else 2

            db.session.commit()

            socketio.emit('update_character', properties_serializer(character), room=self._settlement.id) # type: ignore

        return True
    
    def _upgrade_fort(self, level: str) -> bool:
        random_value = random.randint(0, 1)

        tile_changes = {
            "UPGRADE_FORT_1": [(37, 37, "small_fort")],
            "UPGRADE_FORT_2": [(37, 37, f"fort_top_left_{random_value}"), (38, 37, f"fort_top_right_{random_value}"), (37, 36, f"fort_bottom_left_{random_value}"), (38, 36, f"fort_bottom_right_{random_value}")],
            "UPGRADE_FORT_3": [(36, 38, f"tower_right_{random_value}"), (39, 38, f"tower_left_{random_value}"), (36, 35, f"tower_right_{random_value}"), (39, 35, f"tower_left_{random_value}")],
            "UPGRADE_FORT_4": [(36, 37, "wall_vertical"), (36, 36, "wall_vertical"), (37, 38, "wall_horizontal"), (38, 38, "wall_horizontal"), (39, 37, "wall_vertical"), (39, 36, "wall_vertical"), (37, 35, "wall_horizontal"), (38, 35, "wall_horizontal")]
        }
        
        changes = tile_changes.get(level)

        tiles = []

        if changes:
            for pos_x, pos_y, tile_type in changes:
                tile = Tile.query.filter_by(settlement_id=self._settlement.id, pos_x=pos_x, pos_y=pos_y).first()
                
                tile.tile_type = tile_type

                tiles.append(tile_serializer(tile))

        if level == "UPGRADE_FORT_4":
            for tile in Tile.query.filter_by(settlement_id=self._settlement.id, tile_type="claimed", future="fort").all():
                tiles.append({"tile_index" : random.randint(3, 5), "pos_x" : tile.pos_x, "pos_y" : tile.pos_y})
                
                db.session.delete(tile)

        db.session.commit()

        socketio.emit('update_tiles', tiles, room=self._settlement.id) # type: ignore

        return True

    def _random_house_coordinates(self, tiles) -> tuple[int, int]:
        house_count = Tile.query.filter_by(settlement_id=self._settlement.id, tile_type="hut").count()

        if house_count < 1:
            print("no houses")

            return 0, 0

        house = Tile.query.filter_by(settlement_id=self._settlement.id, tile_type="hut").offset(random.randint(0, house_count - 1)).first()

        if not house:
            print("no random house")

            return 0, 0

        while True:
            pos_x = random.randint(abs(37 - house.pos_x), 33)
            pos_y = random.randint(25, 40)

            exists = False

            for tile in tiles:
                if exists:
                    continue

                if Tile.query.filter_by(settlement_id=self._settlement.id, pos_x=pos_x + tile[0], pos_y=pos_y + tile[1]).first():
                    exists = True

            if not exists:
                break

        return pos_x, pos_y

    def _upgrade_church(self, level: str) -> bool:
        tiles = []

        if level == "UPGRADE_CHURCH_1":
            pos_x, pos_y = self._random_house_coordinates([[0, 0], [1, 0]])

            if not pos_x or not pos_y:
                return False

            tile_1 = Tile(settlement_id=self._settlement.id, pos_x=pos_x, pos_y=pos_y, tile_type="claimed", future="church_chapel")

            db.session.add(tile_1)

            tile_2 = Tile(settlement_id=self._settlement.id, pos_x=pos_x + 1, pos_y=pos_y, tile_type="claimed", future="church_tower")

            db.session.add(tile_2)

            tiles.append(tile_serializer(tile_1))
            tiles.append(tile_serializer(tile_2))

        if level == "UPGRADE_CHURCH_2":
            tile = Tile.query.filter_by(settlement_id=self._settlement.id, future="church_chapel").first()
            
            tile.tile_type = "church_chapel"

            tiles.append(tile_serializer(tile))

        if level == "UPGRADE_CHURCH_3":
            tile = Tile.query.filter_by(settlement_id=self._settlement.id, future="church_tower").first()
            
            tile.tile_type = "church_tower"

            tiles.append(tile_serializer(tile))

        db.session.commit()
        
        socketio.emit('update_tiles', tiles, room=self._settlement.id) # type: ignore

        return True
    
    def _upgrade_bourse(self, level: str) -> bool:
        tiles = []

        if level == "UPGRADE_BOURSE_1":
            coordinates = [[0, 0], [1, 0], [0, 1], [1, 1]]

            pos_x, pos_y = self._random_house_coordinates(coordinates)

            if not pos_x or not pos_y:
                return False
            
            for i in range(len(coordinates)):
                coordinate = coordinates[i]

                tile = Tile(settlement_id=self._settlement.id, pos_x=pos_x + coordinate[0], pos_y=pos_y + coordinate[1], tile_type="claimed", future=f"bourse_{i}")

                db.session.add(tile)
                db.session.commit()

                tiles.append(tile_serializer(tile))

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

        db.session.commit()

        socketio.emit('update_tiles', tiles, room=self._settlement.id) # type: ignore

        return True
    
    def _upgrade_jail(self, level: str) -> bool:
        tiles = []

        if level == "UPGRADE_JAIL_1":
            coordinates = [[0, 0], [1, 0], [0, 1], [1, 1]]

            pos_x, pos_y = self._random_house_coordinates(coordinates)

            if not pos_x or not pos_y:
                return False
            
            for i in range(len(coordinates)):
                coordinate = coordinates[i]

                tile = Tile(settlement_id=self._settlement.id, pos_x=pos_x + coordinate[0], pos_y=pos_y + coordinate[1], tile_type="claimed", future=f"jail_{i}")

                db.session.add(tile)
                db.session.commit()

                tiles.append(tile_serializer(tile))

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

        db.session.commit()

        socketio.emit('update_tiles', tiles, room=self._settlement.id) # type: ignore

        return True

    def _warehouse(self) -> bool:
        pos_x, pos_y = self._random_house_coordinates([0, 0])

        if not pos_x or not pos_y:
            return False
        
        tile = Tile(settlement_id=self._settlement.id, pos_x=pos_x, pos_y=pos_y, tile_type="warehouse")

        db.session.add(tile)
        db.session.commit()

        warehouse = Warehouse(settlement_id=self._settlement.id, tile=tile.id)

        db.session.add(warehouse)
        db.session.commit()

        socketio.emit('update_tiles', [tile_serializer(tile)], room=self._settlement.id) # type: ignore

        return True

    def work(self, current_time: datetime) -> None:
        print(f"{self._ruler.name} {self._ruler.surname} started working")

        if self._ruler.last_action and (self._ruler.last_action + timedelta(days=1)) > current_time and False:
            print("waiting")

            return None
        
        if random.randint(self._characteristics['carelessness'], 100) < 50:
            print("not doing anything")

            return None

        action = self._get_action()

        if not action:
            print("no action")

            return
        
        success = False
        
        if action == Action.CLAIM_LAND:
            success = self._claim_land()
        
        if action == Action.SAVE_TAXES:
            success = self._save_taxes()
        
        if action == Action.COLLECT_TAXES:
            success = self._collect_taxes(current_time)
        
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

        if not success:
            print(f"no success on {action.name}")

            return

        if not action.repeatable:
            self._actions.append(action.name)
            self._ruler.actions = json.dumps(self._actions)

            db.session.commit()

        self._settlement.taxes -= action.price

        print(self._ruler.last_action, current_time)

        self._ruler.last_action = current_time

        db.session.commit()

        print(f"{self._ruler.name} {self._ruler.surname} finished {action.name} for {action.price}")
