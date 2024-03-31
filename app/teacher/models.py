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
            'index' : self.index,
            'fields' : [task_field.get_dict() for task_field in TaskField.query.filter_by(task_id=self.id)]
        }


class TaskField(db.Model):
    __tablename__ = 'task_field'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    field_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)

    def get_dict(self) -> dict:
        options = []

        if self.field_type == "multiplechoice" or self.field_type == "checkboxes" or self.field_type == "connect" or self.type == "order":
            options = [task_option.get_dict() for task_option in TaskOption.query.filter_by(task_field_id=self.id)]

        return { 
            'id' : self.id,
            'task_id' : self.task_id,
            'field_type' : self.field_type,
            'content' : self.content,
            'options' : options
        }


class TaskOption(db.Model):
    __tablename__ = 'option'

    id = db.Column(db.Integer, primary_key=True)
    task_field_id = db.Column(db.Integer, db.ForeignKey('task_field.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def get_dict(self) -> dict:
        return {
            'id' : self.id,
            'task_field_id' : self.task_field_id,
            'content' : self.content
        }
