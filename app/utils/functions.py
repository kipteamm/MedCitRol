from app.game.models import World, Settlement, Character
from app.auth.models import User

from app.extensions import db


settlement_colours = ['cyan', 'lime', 'purple', 'red', 'brown']

def get_presence(world: World, user: User) -> tuple[Settlement, Character]:
    character = Character.query.filter_by(world_id=world.id, user_id=user.id).first()

    if not character:
        settlements = Settlement.query.filter_by(world_id=world.id).all()

        if not settlements:
            settlement = Settlement(world_id=world.id, name="Unnamed", colour=settlement_colours[0])

            db.session.add(settlement)

        elif settlements.count() < len(settlement_colours):
            i = settlements.count()

            for _settlement in settlements:
                if Character.query.filter_by(world=world.id, settlement_id=_settlement.id).count() >= 8:
                    settlement = Settlement(world_id=world.id, name="Unnamed", colour=settlement_colours[i])

                    db.session.add(settlement)

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

        db.session.commit()

        character = Character(world_id=world.id, user_id=user.id, settlement_id=settlement.id)

        db.session.add(character)
        db.session.commit()

    else:
        settlement = Settlement.query.filter_by(world_id=world.id, id=character.settlement_id).first()

    return settlement, character
