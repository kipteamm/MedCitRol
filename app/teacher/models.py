from app.extensions import db

import uuid


def get_uuid():
    return str(uuid.uuid4())


class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    user_id = db.Column(db.String(128), db.ForeignKey('users.id'), nullable=False)
    field_index = db.Column(db.Integer, default=0)


class WorldTask(db.Model):
    __tablename__ = 'world_task'

    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    world_id = db.Column(db.String(128), db.ForeignKey('world.id'), nullable=False)
    task_id = db.Column(db.String(128), db.ForeignKey('task.id'), nullable=False)
    index = db.Column(db.Integer, nullable=False)


class TaskField(db.Model):
    __tablename__ = 'task_field'

    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    task_id = db.Column(db.String(128), db.ForeignKey('task.id'), nullable=False)
    field_index = db.Column(db.Integer, nullable=False)
    field_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)


class TaskOption(db.Model):
    __tablename__ = 'task_option'

    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    task_field_id = db.Column(db.String(128), db.ForeignKey('task_field.id'), nullable=False)
    field_type = db.Column(db.String(50), default="text")
    content = db.Column(db.Text)

    answer = db.Column(db.Boolean, default=False)
    connected = db.Column(db.String(128), db.ForeignKey('task_option.id'))


class TaskUser(db.Model):
    __tablename__ = 'task_user'

    id = db.Column(db.String(128), primary_key=True, default=get_uuid)
    task_id = db.Column(db.String(128), db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.String(128), db.ForeignKey('users.id'), nullable=False)
    
    percentage = db.Column(db.Integer, nullable=False)
