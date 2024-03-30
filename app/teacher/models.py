from app.extensions import db


class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    world_id = db.Column(db.Integer, db.ForeignKey('world.id'), nullable=False)
    index = db.Column(db.Integer, nullable=False)

    def get_dict(self) -> dict:
        return {
            'id' : self.id,
            'world_id' : self.world_id,
            'index' : self.index
        }
    