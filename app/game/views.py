from flask_login import current_user, login_required

from flask import Blueprint, render_template, redirect, url_for, make_response
 
from app.utils.serializers import world_serializer, settlement_serializer, character_serializer, tile_serializer
from app.utils.functions import get_key, generateRandomCoordinates
from app.utils.rulers import Ruler
from app.auth.models import User, UserWorlds
from app.extensions import db, socketio

from .models import World, Settlement, Character, Tile, SettlementRuler, Merchant

from datetime import timedelta

import json


game_blueprint = Blueprint('game', __name__)


settlement_colours = ['cyan', 'lime', 'purple', 'red', 'brown']


def get_presence(world: World, user: User) -> tuple[Settlement, Character]:
    user.active_world = world.id

    db.session.commit()

    character = Character.query.filter_by(world_id=world.id, user_id=user.id).first()

    if not character:
        settlements = Settlement.query.filter_by(world_id=world.id).all()

        if not settlements:
            settlement = Settlement(world_id=world.id, name="Unnamed", colour=settlement_colours[0])

            db.session.add(settlement)
            db.session.commit()

            Ruler().create(settlement.id)

            tile = Tile(settlement_id=settlement.id, pos_x=37, pos_y=37, tile_type="well")
            
            db.session.add(tile)
            db.session.commit()

            merchant = Merchant(settlement_id=settlement.id, merchant_type="grain", end_date=(world.current_time + timedelta(weeks=8)))

            db.session.add(merchant)
            db.session.commit()

        elif len(settlements) < len(settlement_colours):
            i = len(settlements)

            for _settlement in settlements:
                if Character.query.filter_by(world_id=world.id, settlement_id=_settlement.id).count() >= 8:
                    settlement = Settlement(world_id=world.id, name="Unnamed", colour=settlement_colours[i])

                    db.session.add(settlement)
                    db.session.commit()

                    Ruler().create(settlement.id)

                    tile = Tile(settlement_id=settlement.id, pos_x=37, pos_y=37, tile_type="well")
                    
                    db.session.add(tile)
                    db.session.commit()

                    merchant = Merchant(settlement_id=settlement.id, merchant_type="grain", end_date=(world.current_time + timedelta(weeks=8)))

                    db.session.add(merchant)
                    db.session.commit()

                    break

                settlement = _settlement

                i += 1

                break
        else:
            character_counts = []

            for i in range(settlements):
                character_counts[i] = {
                    'characters' : Character.query.filter_by(world_id=world.id, settlement_id=settlements[i].id),
                    'id' : settlements[i].id
                }

            sorted_data = sorted(character_counts, key=lambda x: x['characters'])

            settlement = settlements.query.filter_by(id=sorted_data[i].id)

        character = Character(world_id=world.id, user_id=user.id, settlement_id=settlement.id)

        db.session.add(character)
        db.session.commit()

        pos_x, pos_y = None, None

        while pos_x is None or pos_y is None:
            pos_x, pos_y = generateRandomCoordinates(25, 35, 5, True, settlement.id)

        house = Tile(character_id=character.id, settlement_id=settlement.id, pos_x=pos_x, pos_y=pos_y, tile_type="hut")

        db.session.add(house)
        db.session.commit()

        character.house_id = house.id

        socketio.emit("new_tiles", [tile_serializer(house)], room=settlement.id) # type: ignore

    else:
        settlement = Settlement.query.filter_by(world_id=world.id, id=character.settlement_id).first()

    return settlement, character


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

    #settlement.taxes = 10000

    #db.session.commit()

    tiles = [tile_serializer(tile) for tile in Tile.query.filter_by(settlement_id=settlement.id).all()]

    response = make_response(render_template('game/game.html', tiles=tiles, world=world_serializer(world), settlement=settlement_serializer(settlement), character=character_serializer(character)))

    response.set_cookie('psk', get_key(current_user.id, world.id, settlement.id, character.id))

    return response


@game_blueprint.route('/ruler')
@login_required
def ruler():
    #SettlementRuler.query.filter_by(settlement_id=1).first().actions = "[]"

    #db.session.commit()

    Ruler(SettlementRuler.query.filter_by(settlement_id=1).first()).work(World.query.get(1).current_time)

    return "<h1>yes</h1>"
