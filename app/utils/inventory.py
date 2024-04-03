from app.game.models import InventoryItem
from app.extensions import db, socketio

from typing import Optional


class Inventory:
    BUILDABLE_TYPES = {'farm_land', 'windmill', 'bakery'}

    def __init__(self, room_id: int, settlement_id: Optional[int]=None, character_id: Optional[int]=None) -> None:
        self._room_id = room_id
        self._settlement_id = settlement_id
        self._character_id = character_id

    def _is_buildable(self, item_type: str) -> bool:
        return item_type in self.BUILDABLE_TYPES

    def has_items(self, item_type: str, amount: int) -> bool:
        if self._settlement_id:
            inventory_item = InventoryItem.query.filter_by(settlement_id=self._settlement_id, item_type=item_type).first()

            if not inventory_item:
                return False

            return inventory_item.amount >= amount
        
        inventory_item = InventoryItem.query.filter_by(character_id=self._character_id, item_type=item_type).first()

        if not inventory_item:
            return False
        
        return inventory_item.amount >= amount

    def add_item(self, item_type: str, amount: int) -> None:
        if self._settlement_id:
            inventory_item = InventoryItem.query.filter_by(settlement_id=self._settlement_id, item_type=item_type).first()

            if not inventory_item:
                inventory_item = InventoryItem(settlement_id=self._settlement_id, item_type=item_type, buildable=self._is_buildable(item_type))

                db.session.add(inventory_item)
                db.session.commit()

        else:
            inventory_item = InventoryItem.query.filter_by(character_id=self._character_id, item_type=item_type).first()

            if not inventory_item:
                inventory_item = InventoryItem(character_id=self._character_id, item_type=item_type, buildable=self._is_buildable(item_type))

                db.session.add(inventory_item)
                db.session.commit()

        inventory_item.amount += amount

        db.session.commit()

        data = {
            'is_settlement' : self._settlement_id != None,
            'item' : inventory_item.get_dict()
        }

        socketio.emit('update_inventory', data, room=self._room_id) # type: ignore

    def remove_item(self, item_type: str, amount: int) -> None:
        if self._settlement_id:
            inventory_item = InventoryItem.query.filter_by(settlement_id=self._settlement_id, item_type=item_type).first()

        else:
            inventory_item = InventoryItem.query.filter_by(character_id=self._character_id, item_type=item_type).first()

        if not inventory_item:
            raise ValueError(f"No item {item_type} found in settlement inventory")
            
        if inventory_item.amount < amount:
            raise ValueError(f"Not enough {item_type} in inventory to remove {amount}")
        
        inventory_item.amount -= amount

        db.session.commit()

        data = {
            'is_settlement' : self._settlement_id != None,
            'item' : inventory_item.get_dict()
        }

        socketio.emit('update_inventory', data, room=self._room_id) # type: ignore

    def get_amount(self, item_type: str) -> int:
        try:
            if self._settlement_id:
                return InventoryItem.query.filter_by(settlement_id=self._settlement_id, item_type=item_type).first().amount

            return InventoryItem.query.filter_by(character_id=self._character_id, item_type=item_type).first().amount
        
        except:
            return 0
