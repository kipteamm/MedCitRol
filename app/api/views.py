from flask import Blueprint, request, make_response

from app.teacher.models import Task
from app.game.models import AccessKey, Character

from app.extensions import db


api_blueprint = Blueprint('api', __name__, url_prefix="/api")


@api_blueprint.route("/work", methods=["GET"])
def work():
    authorization = request.headers.get('Authorization')

    access_key = None

    if authorization:
        access_key = AccessKey.query.filter_by(key=authorization).first()

    if not authorization or not access_key:
        return make_response({"error" : "Invalid authentication."}, 401)
    
    character = Character.query.get(access_key.character_id)

    if not character.profession:
        return make_response({"error" : "You have no profession."}, 400)
    
    task = Task.query.filter_by(world_id=access_key.world_id, index=character.task_index).first().get_dict()

    return make_response(task, 200)


@api_blueprint.route("/profession/set", methods=["PUT"])
def set_profession():
    authorization = request.headers.get('Authorization')

    access_key = None

    if authorization:
        access_key = AccessKey.query.filter_by(key=authorization).first()

    if not authorization or not access_key:
        return make_response({"error" : "Invalid authentication."}, 401)
    
    character = Character.query.get(access_key.character_id)

    json = request.json

    if not json or 'profession' not in json:
        return make_response({"error" : "Invalid profession."}, 400)
    
    character.profession = json['profession']

    db.session.commit()

    return make_response({"success" : True}, 204)
