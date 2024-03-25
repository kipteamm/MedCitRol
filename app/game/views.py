from flask import Blueprint, render_template

game_blueprint = Blueprint('game', __name__)


@game_blueprint.route('/home')
def home():
    return render_template("game/home.html")


@game_blueprint.route('/game')
def game():
    return render_template('game/game.html')