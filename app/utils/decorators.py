from functools import wraps
from flask import request, make_response, g

from app.game.models import AccessKey, Character

def character_auhtorized(f):
    @wraps(f)
    def _decorated_function(*args, **kwargs):
        authorization = request.headers.get('Authorization')

        access_key = None

        if authorization:
            access_key = AccessKey.query.filter_by(key=authorization).first()

        if not access_key:
            return make_response({"error" : "Invalid authentication."}, 401)
        
        character = Character.query.get(access_key.character_id)

        if request.path != "/api/character/sleep":
            if character.start_sleep:
                return make_response({"error" : "You are sleeping."}, 400)
            
            if character.jailed and request.path != "/api/character/eat":
                return make_response({"error", "You are in jail."})
        
        g.character = character
        g.access_key = access_key
        
        return f(*args, **kwargs)
    
    return _decorated_function


def authorized(f):
    @wraps(f)
    def _decorated_function(*args, **kwargs):
        authorization = request.headers.get('Authorization')

        access_key = None

        if authorization:
            access_key = AccessKey.query.filter_by(key=authorization).first()

        if not access_key:
            return make_response({"error" : "Invalid authentication."}, 401)
        
        g.access_key = access_key

        return f(*args, **kwargs)
    
    return _decorated_function
