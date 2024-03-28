from flask_socketio import SocketIO, Namespace, join_room, leave_room # type: ignore

from app.utils.functions import authenticated

from app.extensions import db

from .models import World


def register_events(socketio: SocketIO):
    @socketio.on('join')
    def join(data):
        if not authenticated(data):
            return
        
        join_room(data['world_id'])
        join_room(data['settlement_id'])

    return