from flask_login import current_user, login_required

from flask import Blueprint, render_template, redirect, url_for, make_response

from app.utils.inventory import Inventory
from app.utils.functions import get_presence, get_key
from app.extensions import db

from .models import World, Tile


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
    world = World(user_id=current_user.id)

    db.session.add(world)

    current_user.worlds.append(world)

    db.session.commit()

    return redirect(url_for('game.home'))


@game_blueprint.route('/game/<id>')
@login_required
def game(id):
    world = World.query.filter_by(id=id).first()

    if not world:
        return redirect(url_for('game.home'))
    
    world.update_time()

    settlement, character = get_presence(world, current_user) # type: ignore

    tiles = [tile.get_dict() for tile in Tile.query.filter_by(settlement_id=settlement.id).all()]

    response = make_response(render_template('game/game.html', tiles=tiles, world=world, settlement=settlement, character=character))

    response.set_cookie('psk', get_key(current_user.id, world.id, settlement.id, character.id))

    return response
