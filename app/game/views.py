from flask_login import current_user, login_required

from flask import Blueprint, render_template, redirect, url_for

from app.extensions import db

from .models import World, Settlement, Character

game_blueprint = Blueprint('game', __name__)


@game_blueprint.route('/home')
@login_required
def home():
    worlds = []

    for world in current_user.worlds:
        worlds.append({
            'id': world.id,
            'code': world.code
        })

    return render_template("game/home.html", worlds=worlds)


@game_blueprint.route('/game/create')
@login_required
def create_game():
    world = World(current_user.id)

    db.session.add(world)

    current_user.worlds.append(world)

    db.session.commit()

    return redirect(url_for('game.home'))

@game_blueprint.route('/game')
@login_required
def game():
    return render_template('game/game.html')