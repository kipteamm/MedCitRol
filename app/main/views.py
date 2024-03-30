from flask import Blueprint, render_template, redirect

from app.teacher.models import Task

from app.game.models import World, Settlement, Character, AccessKey, Tile

from app.extensions import db


main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    return render_template('main/index.html')


@main_blueprint.route('/reset')
def reset():
    for task in Task.query.all():
        db.session.delete(task)

    for world in World.query.all():
        db.session.delete(world)

    for settlement in Settlement.query.all():
        db.session.delete(settlement)

    for character in Character.query.all():
        db.session.delete(character)

    for access_key in AccessKey.query.all():
        db.session.delete(access_key)

    for tile in Tile.query.all():
        db.session.delete(tile)

    db.session.commit()

    return redirect('/')
