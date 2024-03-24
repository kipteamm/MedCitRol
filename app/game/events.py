from flask_socketio import SocketIO, join_room, leave_room


def register_events(socketio: SocketIO):
    return