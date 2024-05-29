from flask_apscheduler import APScheduler

from flask_migrate import Migrate

from flask_login import LoginManager, current_user, AnonymousUserMixin

from flask import Flask, redirect, url_for, flash, request

from .teacher.views import teacher_blueprint

from .utils.serializers import properties_serializer
from .utils.presence import update_time, update_character, update_settlement

from .auth.models import User
from .auth.views import auth_blueprint

from .game.views import game_blueprint
from .game.events import register_events
from .game.models import World, Character

from .main.views import main_blueprint

from .api.views import api_blueprint

from .extensions import db, socketio

from datetime import datetime


active_connections = {}
active_worlds = []


def create_app():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config["SECRET_KEY"] = "secret"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./database.db'

    app.register_blueprint(teacher_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(game_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint)

    login_manager = LoginManager(app)

    db.init_app(app)

    migrate = Migrate()
    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    @login_manager.unauthorized_handler
    def unauthorized():
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('auth.login'))

    socketio.init_app(app)
    register_events(socketio)

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    @socketio.on('connect')
    def handle_connect():
        if isinstance(current_user, AnonymousUserMixin):
            return

        active_connections[request.sid] = {'id' : current_user.id, 'active_world' : current_user.active_world} # type: ignore

    @socketio.on('disconnect')
    def handle_disconnect():
        if isinstance(current_user, AnonymousUserMixin):
            return

        active_connections.pop(request.sid, None) # type: ignore

    if not scheduler.get_job('update_worlds') and False:
        @scheduler.task('interval', id='update_worlds', minutes=1)
        def update_worlds():
            with app.app_context():
                print(f"[{datetime.now()}] updated worlds")

                worlds = []
                settlements = []
                user_ids = []

                for sid, user in list(active_connections.items()):
                    world = World.query.get(user['active_world'])

                    if not world:
                        continue

                    if user['id'] in user_ids:
                        continue

                    user_ids.append(user['id'])

                    if not user['active_world'] in worlds:
                        update_time(world)

                        socketio.emit('update_time', {'current_time' : world.get_world_time()}, room=world.id) #type: ignore

                        worlds.append(user['active_world'])

                    character = Character.query.filter_by(user_id=user['id'], world_id=user['active_world']).first()

                    update_character(character, world, 1)

                    socketio.emit('update_character', properties_serializer(character), room=character.settlement_id) #type: ignore

                    if character.settlement_id in settlements:
                        continue

                    settlements.append(character.settlement_id)

                    update_settlement(character, world)

                pass

    return app
