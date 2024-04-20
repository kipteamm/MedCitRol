from app.extensions import db


class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    world_id = db.Column(db.Integer, db.ForeignKey('world.id'), nullable=False)
    index = db.Column(db.Integer, nullable=False)


class TaskField(db.Model):
    __tablename__ = 'task_field'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    field_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)


class TaskOption(db.Model):
    __tablename__ = 'task_option'

    id = db.Column(db.Integer, primary_key=True)
    task_field_id = db.Column(db.Integer, db.ForeignKey('task_field.id'), nullable=False)
    content = db.Column(db.Text)

    answer = db.Column(db.Boolean, default=False)
    connected = db.Column(db.Integer, db.ForeignKey('task_option.id'))
