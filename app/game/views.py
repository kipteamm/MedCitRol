from flask_login import current_user, login_required

from flask import Blueprint, render_template, redirect, url_for, make_response, request
 
from app.utils.serializers import world_serializer, settlement_serializer, character_serializer, tile_serializer, settlement_ruler_serializer
from app.utils.functions import get_key
from app.utils.presence import get_presence
from app.utils.rulers import Ruler
from app.auth.models import UserWorlds
from app.extensions import db

from .models import World, Tile, SettlementRuler, Settlement, Character


game_blueprint = Blueprint('game', __name__)


@game_blueprint.route('/game/<id>')
@login_required
def game(id):
    user_world = UserWorlds.query.filter_by(user_id=current_user.id, world_id=id).first()

    if not user_world:
        return redirect(url_for('home.games'))
    
    world = World.query.get(id)

    world.update_time()

    settlement, character = get_presence(world, current_user) # type: ignore

    db.session.commit()

    tiles = [tile_serializer(tile) for tile in Tile.query.filter_by(settlement_id=settlement.id).all()]

    response = make_response(render_template('game/game.html', tiles=tiles, user_id=current_user.id, world=world_serializer(world), settlement=settlement_serializer(settlement), settlement_ruler=settlement_ruler_serializer(SettlementRuler.query.filter_by(settlement_id=settlement.id).first()), character=character_serializer(character)))

    response.set_cookie('psk', get_key(current_user.id, world.id, settlement.id, character.id))

    return response


@game_blueprint.route('/game/<id>/<settlement_id>')
@login_required
def settlement(id, settlement_id):
    user_world = UserWorlds.query.filter_by(user_id=current_user.id, world_id=id).first()

    if not user_world:
        return redirect(url_for('home.games'))
    
    world = World.query.get(id)

    settlement = Settlement.query.filter_by(id=settlement_id, world_id=id).first()

    if not settlement or Character.query.filter_by(user_id=current_user.id, settlement_id=settlement.id).first():
        return redirect(f'/game/{id}')

    tiles = [tile_serializer(tile) for tile in Tile.query.filter_by(settlement_id=settlement.id).all()]

    return render_template('game/settlement.html', tiles=tiles, user_id=current_user.id, world=world_serializer(world), settlement=settlement_serializer(settlement), settlement_ruler=settlement_ruler_serializer(SettlementRuler.query.filter_by(settlement_id=settlement.id).first()))


"""
@game_blueprint.route('/ruler')
@login_required
def ruler():
    #SettlementRuler.query.filter_by(settlement_id=1).first().actions = "[]"

    #db.session.commit()

    current_time = World.query.first().current_time

    for ruler in SettlementRuler.query.all():
        Ruler(ruler).work(current_time)

    return "<h1>yes</h1>"
"""
