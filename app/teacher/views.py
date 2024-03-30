from flask_login import current_user, login_required

from flask import Blueprint, redirect, url_for, render_template

from app.game.models import World

from app.extensions import db


teacher_blueprint = Blueprint('teacher', __name__, url_prefix="/teacher")


@teacher_blueprint.route('/game/<id>')
@login_required
def game(id):
    world = World.query.filter_by(id=id, user_id=current_user.id).first()

    if not world:
        return redirect(url_for('game.home'))

    return render_template('teacher/game.html', world=world)
