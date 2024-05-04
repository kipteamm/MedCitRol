from app.game.models import AccessKey, Tile, Merchant
from app.extensions import db

from datetime import datetime, timezone, timedelta

from typing import Optional

import secrets
import random


def get_key(user_id: int, world_id: Optional[int]=None, settlement_id: Optional[int]=None, character_id: Optional[int]=None) -> str:
    access_key = AccessKey.query.filter_by(user_id=user_id).first()

    now = datetime.now(timezone.utc)

    if not access_key:
        access_key = AccessKey(
            user_id=user_id, 
            world_id=world_id, 
            settlement_id=settlement_id, 
            character_id=character_id,
            key=secrets.token_hex(nbytes=64),
            key_date=now
        )

        db.session.add(access_key)
        db.session.commit()

        return access_key.key
    
    if access_key.key_date.tzinfo is None:
        access_key.key_date = access_key.key_date.replace(tzinfo=timezone.utc)

    expired = access_key.key_date - now > timedelta(hours=12) if access_key.key_date else False

    if expired or not access_key.key:
        access_key.key = secrets.token_hex(nbytes=64)
        access_key.key_date = now

    if settlement_id and not access_key.settlement_id:
        access_key.settlement_id = settlement_id
    
    if character_id and not access_key.character_id:
        access_key.character_id = character_id

    db.session.commit()

    return access_key.key


def get_access_key(key: Optional[str]) -> Optional[AccessKey]:
    if not key:
        return

    access_key = AccessKey.query.filter_by(key=key).first()

    if access_key.key_date.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc) > timedelta(hours=12):
        return
    
    return access_key


def generateRandomCoordinates(center_x: int, center_y: int, deviation: int, empty: bool=False, settlement_id: Optional[int]=None) -> tuple[Optional[int], Optional[int]]:
    pos_x = center_x + random.randint(-deviation, deviation)
    pos_y = center_y + random.randint(-deviation, deviation)

    if not empty:
        return pos_x, pos_y
    
    if not settlement_id:
        return None, None

    if Tile.query.filter_by(settlement_id=settlement_id, pos_x=pos_x, pos_y=pos_y).first():
        return None, None

    return pos_x, pos_y


def get_merchandise(merchant_type: str) -> dict[str, int]:
    if merchant_type == "grain":
        return {"rye" : 2, "rye_flour" : 3, "bread" : 5} 
    
    if merchant_type == "buildable":
        return {"market_stall" : 10}
    
    return {}
