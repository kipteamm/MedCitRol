from flask_login import current_user, login_required

from flask import Blueprint, render_template, redirect, url_for, make_response
 
from app.utils.serializers import world_serializer, settlement_serializer, character_serializer, tile_serializer, settlement_ruler_serializer
from app.utils.functions import get_key
from app.utils.presence import get_presence
from app.utils.rulers import Ruler
from app.auth.models import UserWorlds
from app.extensions import db

from .models import World, Tile, SettlementRuler


game_blueprint = Blueprint('game', __name__)


@game_blueprint.route('/home')
@login_required
def home():
    worlds = []

    for world in current_user.worlds:
        worlds.append({
            'id': world.id,
            'user_id': world.user_id,
            'code': world.code
        })

    return render_template("game/home.html", worlds=worlds)


@game_blueprint.route('/invite/<invite>')
@login_required
def invite(invite):
    world = World.query.filter_by(code=invite).first()

    if not world:
        return redirect(url_for('game.home'))
    
    user_world = UserWorlds.query.filter_by(user_id=current_user.id, world_id=world.id).first()

    if user_world:
        return redirect(f'/game/{user_world.world_id}')
    
    current_user.worlds.append(world)

    db.session.commit()

    return redirect(f'/game/{world.id}')


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
    user_world = UserWorlds.query.filter_by(user_id=current_user.id, world_id=id).first()

    if not user_world:
        return redirect(url_for('game.home'))
    
    world = World.query.get(id)

    world.update_time()

    settlement, character = get_presence(world, current_user) # type: ignore

    db.session.commit()

    tiles = [tile_serializer(tile) for tile in Tile.query.filter_by(settlement_id=settlement.id).all()]

    response = make_response(render_template('game/game.html', tiles=tiles, world=world_serializer(world), settlement=settlement_serializer(settlement), settlement_ruler=settlement_ruler_serializer(SettlementRuler.query.filter_by(settlement_id=settlement.id).first()), character=character_serializer(character)))

    response.set_cookie('psk', get_key(current_user.id, world.id, settlement.id, character.id))

    return response


@game_blueprint.route('/ruler')
@login_required
def ruler():
    #SettlementRuler.query.filter_by(settlement_id=1).first().actions = "[]"

    #db.session.commit()

    Ruler(SettlementRuler.query.filter_by(settlement_id=1).first()).work(World.query.get(1).current_time)

    return "<h1>yes</h1>"
