from flask_socketio import SocketIO, join_room

from app.utils.serializers import tile_serializer
from app.utils.inventory import Inventory
from app.extensions import db

from .models import AccessKey, Tile


def register_events(socketio: SocketIO):
    @socketio.on('join')
    def join(data):
        access_key = AccessKey.query.filter_by(world_id=data['world_id'], user_id=data['user_id'], key=data['access_key']).first()

        if not access_key:
            return
        
        join_room(access_key.world_id)
        
        if access_key.settlement_id != data['settlement_id']:
            return

        join_room(access_key.settlement_id)

        print(f"joined, {access_key.settlement_id}")
