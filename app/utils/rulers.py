from app.utils.serializers import properties_serializer, tile_serializer
from app.utils.functions import get_coordinates
from app.game.models import Settlement, SettlementRuler, Character, Tile
from app.extensions import db, socketio

from datetime import timedelta

from typing import Optional

from enum import Enum

import random
import json
import math


CHARACTERISTICS = ['tyranny', 'economy', 'religion', 'social', 'military', 'carelessness']


class Action(Enum):
    CLAIM_LAND = {"characteristics": ["tyranny", "military"], "price": 0, "previous" : None, "repeatable" : False}
    SAVE_TAXES = {"characteristics": ["social", "economy"], "price": 0, "previous" : None, "repeatable" : True}
    COLLECT_TAXES = {"characteristics": ["tyranny", "military", "religion", "economy"], "price": 0, "previous" : None, "repeatable" : True}
    #UPGRADE_FORT_1 = {"characteristics": ["tyranny", "military"], "price": 10, "previous" : None, "repeatable" : False}
    #UPGRADE_FORT_2 = {"characteristics": ["tyranny", "military"], "price": 30, "previous" : "UPGRADE_FORT_1", "repeatable" : False}
    #UPGRADE_FORT_3 = {"characteristics": ["tyranny", "military"], "price": 60, "previous" : "UPGRADE_FORT_2", "repeatable" : False}
    #UPGRADE_FORT_4 = {"characteristics": ["tyranny", "military"], "price": 90, "previous" : "UPGRADE_FORT_3", "repeatable" : False}
    #UPGRADE_FORT_5 = {"characteristics": ["tyranny", "military"], "price": 120, "previous" : "UPGRADE_FORT_4", "repeatable" : False}
    #UPGRADE_CHURCH_1 = {"characteristics": ["religion", "social"], "price": 10, "previous" : None, "repeatable" : False}
    #UPGRADE_CHURCH_2 = {"characteristics": ["religion", "social"], "price": 30, "previous" : "UPGRADE_CHURCH_1", "repeatable" : False}
    #TRADEROUTE = {"characteristics": ["economy", "social"], "price": 0, "previous" : None, "repeatable" : True}
    #HALLMARK = {"characteristics": ["social", "economy"], "price": 0, "previous" : None, "repeatable" : True}
    #UPGRADE_BOURSE_1 = {"characteristics": ["economy"], "price": 10, "previous" : None, "repeatable" : False}
    #UPGRADE_BOURSE_2 = {"characteristics": ["economy"], "price": 30, "previous" : "UPGRADE_BOURSE_1", "repeatable" : False}
    #UPGRADE_BOURSE_3 = {"characteristics": ["economy"], "price": 60, "previous" : "UPGRADE_BOURSE_2", "repeatable" : False}
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
            self._taxes = Settlement.query.filter_by(id=ruler.settlement_id).first().taxes

    def create(self, settlement_id: int) -> None:
        random.shuffle(CHARACTERISTICS)
        points_left = 300

        for i in range(len(CHARACTERISTICS) - 1):
            random_value = random.randint(0, min(points_left, 100))
            self._characteristics[CHARACTERISTICS[i]] = random_value
            points_left -= random_value

        self._characteristics[CHARACTERISTICS[-1]] = points_left

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

            if action.price > self._taxes:
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
    
    def _claim_land(self) -> None:
        radius = random.randint(2, 3) if self._characteristics['tyranny'] > self._characteristics['social'] else 2

        coordinates = get_coordinates(37, 37, radius)

        tiles = []

        for coordinate in coordinates:
            if Tile.query.filter_by(pos_x=coordinate[0], pos_y=coordinate[1]).first():
                continue

            tile = Tile(pos_x=coordinate[0], pos_y=coordinate[1], settlement_id=self._ruler.settlement_id, tile_type="claimed")

            db.session.add(tile)

            tiles.append(tile_serializer(tile))

        socketio.emit('update_tiles', tiles, room=self._ruker.settlement_id) # type: ignore

        db.session.commit()

        return
    
    def _save_taxes(self) -> None:
        self._taxes = self._taxes + math.ceil(self._taxes * 0.1) + (1 if self._taxes == 0 else 0)

        Settlement.query.get(self._ruler.settlement_id).taxes = self._taxes

        db.session.commit()

        return
    
    def _collect_taxes(self) -> None:
        for character in Character.query.filter_by(settlement_id=self._ruler.settlement_id).all():
            if character.taxes > 0:
                # jail character

                continue

            character.taxes = random.randint(2, 3) if self._characteristics['tyranny'] > self._characteristics['social'] else 2

            db.session.commit()

            socketio.emit('update_character', properties_serializer(character), room=self._ruler.settlement_id) # type: ignore

        return

    def work(self, current_time) -> None:
        print(f"{self._ruler.name} {self._ruler.surname} started working")

        if self._ruler.last_action and (self._ruler.last_action + timedelta(days=2)) > current_time:
            print("waiting")

            return None
        
        if random.randint(self._characteristics['carelessness'], 100) < 50:
            print("not doing anything")

            return None

        action = self._get_action()

        if not action:
            print("no action")

            return
        
        if not action.repeatable:
            self._ruler.actions = json.dumps(self._actions.append(action.name))

            db.session.commit()

        self._ruler.last_action = current_time

        db.session.commit()

        print(f"{self._ruler.name} {self._ruler.surname} finished {action.name}")
        
        if action == Action.CLAIM_LAND:
            return self._claim_land()
        
        if action == Action.SAVE_TAXES:
            return self._save_taxes()
        
        if action == Action.COLLECT_TAXES:
            return self._collect_taxes()
        
        # ...
