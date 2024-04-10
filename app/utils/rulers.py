from app.game.models import SettlementRuler
from app.extensions import db

from typing import Optional

import random
import json

CHARACTERISTICS = ['tyranny', 'economy', 'religion', 'social', 'carelessness']

class Ruler:
    def __init__(self, ruler: Optional[SettlementRuler]=None) -> None:
        self.characteristics = {char: 0 for char in CHARACTERISTICS}

        if ruler:
            for char in CHARACTERISTICS:
                setattr(self, char, getattr(ruler, char))

    def create(self, settlement_id: int) -> None:
        random.shuffle(CHARACTERISTICS)
        points_left = 250

        for i in range(len(CHARACTERISTICS) - 1):
            random_value = random.randint(0, min(points_left, 100))
            self.characteristics[CHARACTERISTICS[i]] = random_value
            points_left -= random_value

        self.characteristics[CHARACTERISTICS[-1]] = points_left

        with open('app/static/data/names.json') as json_file:
            first_name = random.choice(json.load(json_file))

        with open('app/static/data/surnames.json') as json_file:
            last_name = random.choice(json.load(json_file))

        ruler = SettlementRuler(
            settlement_id=settlement_id,
            name=first_name,
            surname=last_name,
            **self.characteristics
        )

        db.session.add(ruler)
        db.session.commit()
