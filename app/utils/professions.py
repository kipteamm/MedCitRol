from app.utils.serializers import tile_serializer
from app.utils.inventory import Inventory
from app.game.models import Character, Farmer, World, Tile, Warehouse, InventoryItem
from app.extensions import db, socketio

from sqlalchemy import func

from datetime import timedelta

import random


class Profession:
    def __init__(self, character: Character) -> None:
        self._character = character

    def _update_tiles(self, tiles: list[Tile], tile_type: str) -> None:
        new_tiles = []

        for tile in tiles:
            tile.tile_type = tile_type

            db.session.commit()

            new_tiles.append(tile_serializer(tile))
            
        socketio.emit('update_tiles', new_tiles, room=self._character.settlement_id) # type: ignore
        

    def _farmer(self) -> None:
        print("farmer worked")

        farmer = Farmer.query.filter_by(character_id=self._character.id).first()
        current_time = World.query.get(self._character.world_id).current_time

        if not farmer: 
            farmer = Farmer(character_id=self._character.id, date=(current_time + timedelta(days=random.randint(93, 124))))

            db.session.add(farmer)
            db.session.commit()

        tiles = Tile.query.filter_by(settlement_id=self._character.settlement_id, character_id=self._character.id, tile_type=farmer.stage).all()

        if not tiles:
            socketio.emit("alert", {"id" : self._character.id, "type" : "error", "message" : "You need to place your farmland first (see build menu)."}, room=self._character.settlement_id) # type: ignore

            return

        if farmer.stage == "farm_land":
            self._update_tiles(tiles, "rye_seeds")

            farmer.stage = "rye_seeds"

            db.session.commit()

            return
        
        if current_time >= farmer.date:
            self._update_tiles(tiles, "farm_land")

            db.session.delete(farmer)
            db.session.commit()

            Inventory(self._character.settlement_id, None, self._character.id).add_item("rye", len(tiles) * random.randint(5, 7))

            socketio.emit("alert", {"id" : self._character.id, "type" : "success", "message" : "You had a successfull harvest."}, room=self._character.settlement_id) # type: ignore

            return

        farmer.date -= timedelta(days=21)

        db.session.commit()

        time_difference = farmer.date - current_time

        print(current_time, farmer.date, time_difference.days)

        if time_difference.days < 36:  
            self._update_tiles(tiles, "rye_harvestable")

            farmer.stage = "rye_harvestable"

        elif time_difference.days < 72 and farmer.stage != "rye_growing":
            self._update_tiles(tiles, "rye_growing")

            farmer.stage = "rye_growing"

        elif time_difference.days >= 72 and farmer.stage != "rye_seeds":
            self._update_tiles(tiles, "rye_seeds")

            farmer.stage = "rye_seeds"

        db.session.commit()

    def _miller(self) -> None:
        print("miller worked")

        tile = Tile.query.filter_by(settlement_id=self._character.settlement_id, character_id=self._character.id, tile_type="windmill").first()

        if not tile:
            socketio.emit("alert", {"id" : self._character.id, "type" : "error", "message" : "You need to build your mind first (see build menu)."}, room=self._character.settlement_id) # type: ignore

            return
        
        inventory = Inventory(self._character.settlement_id, None, self._character.id)
        
        amount = min(inventory.get_amount("rye"), 4)

        if amount > 0:
            inventory.remove_item("rye", amount)
            inventory.add_item("rye_flour", random.randint(3, 4) * amount)

        return
    
    def _baker(self) -> None:
        print("baker worked")

        tile = Tile.query.filter_by(settlement_id=self._character.settlement_id, character_id=self._character.id, tile_type="bakery").first()

        if not tile:
            socketio.emit("alert", {"id" : self._character.id, "type" : "error", "message" : "You need to build your bakery first (see build menu)."}, room=self._character.settlement_id) # type: ignore

            return
        
        inventory = Inventory(self._character.settlement_id, None, self._character.id)
        
        amount = min(inventory.get_amount("rye_flour"), 16)

        if amount > 0:
            inventory.remove_item("rye_flour", amount)
            inventory.add_item("bread", amount)

        return
    
    def _merchant(self) -> None:
        print("merchant worked")

        tile = Tile.query.filter_by(settlement_id=self._character.settlement_id, character_id=self._character.id, tile_type="merchant_stall").first()

        if not tile:
            socketio.emit("alert", {"id" : self._character.id, "type" : "error", "message" : "You need to build your merchant stall first (see build menu)."}, room=self._character.settlement_id) # type: ignore

            return

        warehouse = Warehouse.query.filter(Warehouse.settlement_id == self._character.settlement_id, Warehouse.capacity < 100, Warehouse.capacity > 0).ordre_by(func.random()).first()

        if not warehouse:
            return
        
        inventory_item = InventoryItem.query.filter_by(settlement_id=self._character.settlement_id, warehouse_id=warehouse.id).order_by(func.random()).first()

        if not inventory_item:
            return
        
        amount = min(warehouse.capacity + random.randint(2, 6), 100)

        inventory_item.amount += amount
        warehouse.capacity += amount
        
        self._character.pennies += 12

        db.session.commit()

        return
    
    def _weaver(self) -> None:
        print("weaver worked")

        tile = Tile.query.filter_by(settlement_id=self._character.settlement_id, character_id=self._character.id, tile_type="weaver").first()

        if not tile:
            socketio.emit("alert", {"id" : self._character.id, "type" : "error", "message" : "You need to build your weaver first (see build menu)."}, room=self._character.settlement_id) # type: ignore

            return

        inventory = Inventory(self._character.settlement_id, None, self._character.id)
        
        amount = random.randint(1, 4)

        inventory.add_item("clothing", amount)

        return
    
    def _goldsmith(self) -> None:
        print("goldsmith worked")

        tile = Tile.query.filter_by(settlement_id=self._character.settlement_id, character_id=self._character.id, tile_type="goldsmith").first()

        if not tile:
            socketio.emit("alert", {"id" : self._character.id, "type" : "error", "message" : "You need to build your goldsmith first (see build menu)."}, room=self._character.settlement_id) # type: ignore

            return

        inventory = Inventory(self._character.settlement_id, None, self._character.id)
        
        amount = random.randint(1, 2)

        if amount > 0:
            inventory.add_item("jewelry", amount)

        return

    def work(self) -> None:
        if self._character.profession == "farmer":
            return self._farmer()
        
        if self._character.profession == "miller":
            return self._miller()
        
        if self._character.profession == "baker":
            return self._baker()
        
        if self._character.profession == "merchant":
            return self._merchant()

        if self._character.profession == "weaver":
            return self._weaver()

        if self._character.profession == "goldsmith":
            return self._goldsmith()
