from flask import Blueprint, render_template

game_blueprint = Blueprint('game', __name__)


@game_blueprint.route('/game')
def game():
    return render_template('game/game.html')