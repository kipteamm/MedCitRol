from app.utils.serializers import inventory_item_serializer
from app.game.models import InventoryItem
from app.extensions import db, socketio

from typing import Optional


class Inventory:
    BUILDABLE_TYPES = {'farm_land', 'windmill', 'bakery', 'market_stall', 'merchant_stall', 'weaver', 'goldsmith'}

    def __init__(self, room_id: int, warehouse_id: Optional[int]=None, character_id: Optional[int]=None) -> None:
        self._room_id = room_id
        self._warehouse_id = warehouse_id
        self._character_id = character_id

    def is_buildable(self, item_type: str) -> bool:
        return item_type in self.BUILDABLE_TYPES

    def has_items(self, item_type: str, amount: int) -> bool:
        if self._warehouse_id:
            inventory_item = InventoryItem.query.filter_by(warehouse_id=self._warehouse_id, item_type=item_type).first()

            if not inventory_item:
                return False

            return inventory_item.amount >= amount
        
        inventory_item = InventoryItem.query.filter_by(character_id=self._character_id, item_type=item_type).first()

        if not inventory_item:
            return False
        
        return inventory_item.amount >= amount

    def add_item(self, item_type: str, amount: int) -> None:
        if self._warehouse_id:
            inventory_item = InventoryItem.query.filter_by(warehouse_id=self._warehouse_id, item_type=item_type).first()

            if not inventory_item:
                inventory_item = InventoryItem(settlement_id=self._room_id, warehouse_id=self._warehouse_id, item_type=item_type, buildable=self.is_buildable(item_type))

                db.session.add(inventory_item)
                db.session.commit()

        else:
            inventory_item = InventoryItem.query.filter_by(character_id=self._character_id, item_type=item_type).first()

            if not inventory_item:
                inventory_item = InventoryItem(settlement_id=self._room_id, character_id=self._character_id, item_type=item_type, buildable=self.is_buildable(item_type))

                db.session.add(inventory_item)
                db.session.commit()

        inventory_item.amount += amount

        db.session.commit()

        data = {
            'character_id' : self._character_id,
            'warehouse_id' : self._warehouse_id,
            'item' : inventory_item_serializer(inventory_item),
            'deleted' : False
        }

        socketio.emit('update_inventory', data, room=self._room_id) # type: ignore

    def remove_item(self, item_type: str, amount: int) -> None:
        if self._warehouse_id:
            inventory_item = InventoryItem.query.filter_by(warehouse_id=self._warehouse_id, item_type=item_type).first()

        else:
            inventory_item = InventoryItem.query.filter_by(character_id=self._character_id, item_type=item_type).first()

        if not inventory_item:
            raise ValueError(f"No item {item_type} found in {'any warehouses' if self._warehouse_id else 'character'} inventory")
            
        if inventory_item.amount < amount:
            raise ValueError(f"Not enough {item_type} in inventory to remove {amount}")
        
        inventory_item.amount -= amount

        db.session.commit()

        item_data = inventory_item_serializer(inventory_item)

        deleted = inventory_item.amount <= 0

        if inventory_item.amount <= 0:
            db.session.delete(inventory_item)
            db.session.commit()
            
        data = {
            'character_id' : self._character_id,
            'warehouse_id' : self._warehouse_id,
            'item' : item_data,
            'deleted' : deleted,
        }

        socketio.emit('update_inventory', data, room=self._room_id) # type: ignore

    def get_amount(self, item_type: str) -> int:
        try:
            if self._warehouse_id:
                return InventoryItem.query.filter_by(warehouse_id=self._warehouse_id, item_type=item_type).first().amount

            return InventoryItem.query.filter_by(character_id=self._character_id, item_type=item_type).first().amount
        
        except:
            return 0
