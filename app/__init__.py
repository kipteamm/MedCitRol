from flask_apscheduler import APScheduler

from flask_login import LoginManager

from flask_migrate import Migrate

from flask import Flask, redirect, url_for, flash

from .auth.models import User
from .auth.views import auth_blueprint

from .game.views import game_blueprint
from .game.events import register_events
from .game.models import World

from .main.views import main_blueprint

from .extensions import db, socketio

from datetime import datetime, timedelta


def create_app():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config["SECRET_KEY"] = "secret"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./database.db'

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(game_blueprint)
    app.register_blueprint(main_blueprint)

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

    if not scheduler.get_job('update_time') and False:
        @scheduler.task('interval', id='update_time', minutes=1)
        def update_time():
            with app.app_context():
                print(f"[{datetime.now()}] updated time")

                worlds = World.query.all()
                
                for world in worlds:
                    world.current_time += timedelta(hours=1)

                db.session.commit()

                pass

    return app
