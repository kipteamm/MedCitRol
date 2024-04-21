from flask import Blueprint, render_template, redirect, send_from_directory, request, make_response

from app.utils.functions import get_access_key
from app.teacher.models import Task, TaskField, TaskOption
from app.game.models import World, Settlement, SettlementRuler, Character, AccessKey, Tile, InventoryItem, Farmer, MarketItem, Merchant
from app.extensions import db

import os


main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    return render_template('main/index.html')


@main_blueprint.route('/help')
def help():
    return render_template('main/help.html')


@main_blueprint.route('/reset')
def reset():
    for task in Task.query.all():
        db.session.delete(task)

    for task_field in TaskField.query.all():
        db.session.delete(task_field)

    for task_option in TaskOption.query.all():
        db.session.delete(task_option)

    for world in World.query.all():
        db.session.delete(world)

    for settlement in Settlement.query.all():
        db.session.delete(settlement)

    for settlement_ruler in SettlementRuler.query.all():
        db.session.delete(settlement_ruler)

    for character in Character.query.all():
        db.session.delete(character)

    for access_key in AccessKey.query.all():
        db.session.delete(access_key)

    for tile in Tile.query.all():
        db.session.delete(tile)

    for item in InventoryItem.query.all():
        db.session.delete(item)

    for farmer in Farmer.query.all():
        db.session.delete(farmer)

    for item in MarketItem.query.all():
        db.session.delete(item)

    for merchant in Merchant.query.all():
        db.session.delete(merchant)

    db.session.commit()

    return redirect('/')


@main_blueprint.route('/media/tasks/<path:filename>')
def serve_task_image(filename):
    if not get_access_key(request.args.get('psk')):
        return make_response({"error" : "Invalid authorization"}, 401)

    tasks_dir = os.path.join(os.getcwd(), 'media', 'tasks')

    return send_from_directory(tasks_dir, filename)