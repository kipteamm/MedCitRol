from flask_apscheduler import APScheduler

from flask_migrate import Migrate

from flask_login import LoginManager, current_user, AnonymousUserMixin

from flask import Flask, redirect, url_for, flash, request

from .teacher.views import teacher_blueprint

from .utils.serializers import properties_serializer
from .utils.presence import add_merchant
from .utils.rulers import Ruler

from .auth.models import User
from .auth.views import auth_blueprint

from .game.views import game_blueprint
from .game.events import register_events
from .game.models import World, Settlement, SettlementRuler, Character, Merchant

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
    #app.config["DEBUG"] = True
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
        if isinstance(current_user, AnonymousUserMixin):
            return

        active_connections[request.sid] = {'id' : current_user.id, 'active_world' : current_user.active_world} # type: ignore

    @socketio.on('disconnect')
    def handle_disconnect():
        if isinstance(current_user, AnonymousUserMixin):
            return

        active_connections.pop(request.sid, None) # type: ignore

    if not scheduler.get_job('update_worlds'):
        @scheduler.task('interval', id='update_worlds', minutes=1)
        def update_worlds():
            with app.app_context():
                print(f"[{datetime.now()}] updated worlds")

                worlds = []
                settlements = []
                user_ids = []

                for sid, user in active_connections.items():
                    world = World.query.get(user['active_world'])

                    if user['id'] in user_ids:
                        continue

                    user_ids.append(user['id'])

                    if not user['active_world'] in worlds:
                        world.current_time += timedelta(hours=1)
                        world.last_time_update = datetime.now()

                        db.session.commit()

                        socketio.emit('update_time', {'current_time' : world.get_world_time()}, room=world.id) #type: ignore

                        worlds.append(user['active_world'])

                    character = Character.query.filter_by(user_id=user['id'], world_id=user['active_world']).first()
                    character.last_update = world.current_time

                    if character.jailed and world.current_time >= character.jail_end:
                        character.jailed = False
                        character.jail_end = None

                    else:
                        if character.hunger > 0:
                            character.hunger -= 1
                    
                        if character.hunger <= 0 and character.health > 0:
                            character.health -= 1

                        if character.start_sleep and world.current_time >= character.end_sleep:
                            character.fatigue += math.floor((character.end_sleep - character.start_sleep).total_seconds() / 3600) + 1

                            character.start_sleep = None

                            character.health += 6

                        elif character.fatigue > 0:
                            character.fatigue -= 1

                        elif character.fatigue <= 0 and character.health > 0:
                            character.health -= 1

                        if character.fatigue < 7 and random.randint(1, 4) == 2 and not character.start_sleep:
                            socketio.emit("close_eyes", {"id" : character.id}, room=character.settlement_id) # type: ignore

                            character.health -= 1

                    socketio.emit('update_character', properties_serializer(character), room=character.settlement_id) #type: ignore

                    if character.settlement_id in settlements:
                        continue

                    settlements.append(character.settlement_id)

                    settlement_ruler = SettlementRuler.query.filter_by(settlement_id=character.settlement_id).first()

                    Ruler(settlement_ruler).work(world.current_time)

                    merchant = Merchant.query.filter_by(settlement_id=character.settlement_id).first()

                    if merchant and merchant.end_date < world.current_time:
                        db.session.delete(merchant)

                        socketio.emit("merchant_leave", room=character.settlement_id) # type: ignore

                    elif not merchant and random.randint(1, 24) == 13:
                        add_merchant(character.settlement_id, world.current_time, random.randint(2, 6))

                    settlement = Settlement.query.filter(Settlement.id == character.settlement_id, Settlement.revolution == True, Settlement.revolution_start + timedelta(days=1) <= world.current_time).first()

                    if not settlement:
                        continue
                    
                    if random.randint(1, 10) == 5:
                        settlement.revolution = False
                        settlement.revolution_start = None

                        db.session.delete(settlement_ruler)
                        db.session.commit()

                        Ruler().create(settlement.id)

                        socketio.emit('alert', {'type' : "sucess", 'message' : "The revolution has ended and a new ruler has been chosen"}, room=character.settlement_id) #type: ignore

                        for character in Character.query.filter_by(settlement_id=settlement.id, revolutionary=True).all():
                            character.revolutionary = False

                        db.session.commit()

                        continue

                    for character in Character.query.filter_by(settlement_id=settlement.id, revolutionary=True).all():
                        character.jailed = True
                        character.jail_end = world.current_time + timedelta(hours=random.randint(12, 24))
                        character.taxes = 0
                        character.happiness -= max(0, character.happiness - 6)

                db.session.commit()

                pass

    return app
