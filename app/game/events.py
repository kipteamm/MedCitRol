from flask_socketio import SocketIO, Namespace, join_room, leave_room # type: ignore

from app.extensions import db

from .models import World


def register_events(socketio: SocketIO):
    return