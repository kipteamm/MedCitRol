from flask_socketio import SocketIO, join_room

from app.utils.serializers import tile_serializer
from app.utils.inventory import Inventory
from app.utils.functions import authenticated
from app.extensions import db

from .models import Tile


def register_events(socketio: SocketIO):
    @socketio.on('join')
    def join(data):
        if not authenticated(data):
            return
        
        join_room(data['world_id'])
        join_room(data['settlement_id'])

    @socketio.on('build')
    def build(data):
        if not authenticated(data):
            return
        
        inventory = Inventory(data['settlement_id'], None, data['character_id'])

        tiles = []

        for tile in data['event_data']:
            if not inventory.has_items(tile['tile_type'], 1):
                continue

            if Tile.query.filter_by(settlement_id=data['settlement_id'], pos_x=tile['pos_x'], pos_y=tile['pos_y']).first():
                continue

            inventory.remove_item(tile['tile_type'], 1)

            tile = Tile(character_id=data['character_id'], settlement_id=data['settlement_id'], pos_x=tile['pos_x'], pos_y=tile['pos_y'], tile_type=tile['tile_type'])

            db.session.add(tile)
            db.session.commit()

            tiles.append(tile_serializer(tile))
            
        socketio.emit('new_tiles', tiles, room=data['world_id']) # type: ignore
