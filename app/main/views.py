from flask_login import current_user, AnonymousUserMixin

from flask import Blueprint, render_template, redirect, send_from_directory, request, make_response

from app.utils.functions import get_access_key
from app.teacher.models import Task, WorldTask, TaskField, TaskOption
from app.game.models import World, Settlement, SettlementRuler, Character, AccessKey, Tile, InventoryItem, Farmer, MarketItem, Merchant, Warehouse, TraderouteRequest
from app.auth.models import UserWorlds
from app.extensions import db

import json
import os


main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    red = request.args.get('red')

    if isinstance(current_user, AnonymousUserMixin) or (red != 'true' and red != None):
        return render_template('main/index.html', user=current_user)
    
    return redirect('/games')


@main_blueprint.route('/help')
def help():
    return render_template('main/help.html')


"""
@main_blueprint.route('/reset')
def reset():
    Task.query.delete()
    WorldTask.query.delete()
    TaskField.query.delete()
    TaskOption.query.delete()
    World.query.delete()
    Settlement.query.delete()
    SettlementRuler.query.delete()
    Character.query.delete()
    AccessKey.query.delete()
    Tile.query.delete()
    InventoryItem.query.delete()
    Farmer.query.delete()
    MarketItem.query.delete()
    Merchant.query.delete()
    UserWorlds.query.delete()
    Warehouse.query.delete()
    TraderouteRequest.query.delete()

    db.session.commit()

    return redirect('/')
"""


@main_blueprint.route('/media/tasks/<path:filename>')
def serve_task_image(filename):
    if not get_access_key(request.args.get('psk')):
        return make_response({"error" : "Invalid authorization"}, 401)

    tasks_dir = os.path.join(os.getcwd(), 'media', 'tasks')

    return send_from_directory(tasks_dir, filename)