from flask_apscheduler import APScheduler

from flask_migrate import Migrate

from flask_login import LoginManager, current_user

from flask import Flask, redirect, url_for, flash, request

from .teacher.views import teacher_blueprint

from .utils.serializers import properties_serializer
from .utils.rulers import Ruler

from .auth.models import User
from .auth.views import auth_blueprint

from .game.views import game_blueprint
from .game.events import register_events
from .game.models import World, SettlementRuler, Character, Merchant

from .main.views import main_blueprint

from .api.views import api_blueprint

from .extensions import db, socketio

from datetime import datetime, timedelta

import random
import math


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
        # Implement the logic to load the user object from the user ID
        return User.query.get(int(user_id))

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
        active_connections[request.sid] = {'id' : current_user.id, 'active_world' : current_user.active_world} # type: ignore

    @socketio.on('disconnect')
    def handle_disconnect():
        active_connections.pop(request.sid, None) # type: ignore

    if not scheduler.get_job('update_worlds') and False:
        @scheduler.task('interval', id='update_worlds', minutes=1)
        def update_worlds():
            with app.app_context():
                print(f"[{datetime.now()}] updated worlds")

                worlds = []
                settlements = []
                user_ids = []

                for sid, user in active_connections.items():
                    world = World.query.get(user['active_world'])

                    if not user['active_world'] in worlds:
                        world.current_time += timedelta(hours=1)
                        world.last_time_update = datetime.now()

                        db.session.commit()

                        socketio.emit('update_time', {'current_time' : world.get_world_time()}, room=world.id) #type: ignore

                        worlds.append(user['active_world'])

                    if user['id'] in user_ids:
                        continue

                    character = Character.query.filter_by(user_id=user['id'], world_id=user['active_world']).first()

                    character.last_update = world.current_time

                    if character.hunger > 0:
                        character.hunger -= 1

                    if character.health > 0:
                        character.health -= 0.25

                    if character.start_sleep:
                        if world.current_time >= character.end_sleep:
                            character.fatigue += math.floor((character.end_sleep - character.start_sleep).total_seconds() / 3600) + 1

                            character.start_sleep = None

                    elif character.fatigue > 0:
                        character.fatigue -= 1

                    if character.fatigue < 7 and random.randint(1, 4) == 2 and not character.start_sleep:
                        socketio.emit("close_eyes", {"id" : character.id}, room=character.settlement_id) # type: ignore

                    if character.jailed:
                        if world.current_time >= character.end_jail:
                            character.jailed = False
                            character.end_jail = None

                    if not character.settlement_id in settlements:
                        settlement_ruler = SettlementRuler.query.filter_by(settlement_id=character.settlement_id).first()

                        if not settlement_ruler.last_action or settlement_ruler.last_action + timedelta(days=1) < world.current_time:
                            Ruler(settlement_ruler).work(world.current_time)

                        settlements.append(character.settlement_id)

                        merchant = Merchant.query.filter(
                            Merchant.settlement_id == character.settlement_id,
                            Merchant.end_date < world.current_time
                        ).first()

                        if merchant:
                            db.session.delete(merchant)

                            socketio.emit("merchant_leave", room=character.settlement_id) # type: ignore

                    socketio.emit('update_character', properties_serializer(character), room=character.settlement_id) #type: ignore

                    user_ids.append(user['id'])

                db.session.commit()

                pass

    return app
