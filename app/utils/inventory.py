from app.game.models import InventoryItem
from app.extensions import db

from typing import Optional


class Inventory:
    BUILDABLE_TYPES = {'farm_land'}

    def __init__(self, settlement_id: Optional[int]=None, character_id: Optional[int]=None) -> None:
        self.settlement_id = settlement_id
        self.character_id = character_id

    def _is_buildable(self, item_type: str) -> bool:
        return item_type in self.BUILDABLE_TYPES

    def add_item(self, item_type: str, amount: int) -> None:
        if self.settlement_id:
            inventory_item = InventoryItem.query.filter_by(settlement_id=self.settlement_id, item_type=item_type).first()

            if not inventory_item:
                inventory_item = InventoryItem(settlement_id=self.settlement_id, item_type=item_type, buildable=self._is_buildable(item_type))

                db.session.add(inventory_item)
                db.session.commit()

        else:
            inventory_item = InventoryItem.query.filter_by(character_id=self.character_id, item_type=item_type).first()

            if not inventory_item:
                inventory_item = InventoryItem(character_id=self.character_id, item_type=item_type, buildable=self._is_buildable(item_type))

                db.session.add(inventory_item)
                db.session.commit()

        inventory_item.amount += amount

        db.session.commit()

    def remove_item(self, item_type: str, amount: int) -> None:
        if self.settlement_id:
            inventory_item = InventoryItem.query.filter_by(settlement_id=self.settlement_id, item_type=item_type).first()

        else:
            inventory_item = InventoryItem.query.filter_by(character_id=self.character_id, item_type=item_type).first()

        if not inventory_item:
            raise ValueError(f"No item {item_type} found in settlement inventory")
            
        if inventory_item.amount < amount:
            raise ValueError(f"Not enough {item_type} in inventory to remove {amount}")
        
        inventory_item.amount -= amount

        db.session.commit()