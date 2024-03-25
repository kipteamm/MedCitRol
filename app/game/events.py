from flask_socketio import SocketIO, join_room, leave_room

from app.extensions import db

from .models import World


def register_events(socketio: SocketIO):
    return