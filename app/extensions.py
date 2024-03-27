from flask_sqlalchemy import SQLAlchemy

from flask_socketio import SocketIO 

socketio = SocketIO(logger=True, engineio_logger=True)

db = SQLAlchemy()