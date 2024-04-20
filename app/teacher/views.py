from flask_login import current_user, login_required

from flask import Blueprint, redirect, url_for, render_template, make_response

from app.utils.serializers import task_serializer
from app.utils.functions import get_key
from app.game.models import World
from app.extensions import db

from .models import Task, TaskField, TaskOption

import os


teacher_blueprint = Blueprint('teacher', __name__, url_prefix="/teacher")


@teacher_blueprint.route('/<world_id>/game')
@login_required
def game(world_id):
    world = World.query.filter_by(id=world_id, user_id=current_user.id).first()

    if not world:
        return redirect(url_for('game.home'))

    return render_template('teacher/game.html', world=world)


@teacher_blueprint.route('/<world_id>/tasks')
@login_required
def tasks(world_id):
    world = World.query.filter_by(id=world_id, user_id=current_user.id).first()

    if not world:
        return redirect(url_for('game.home'))
    
    tasks = Task.query.filter_by(world_id=world.id).all()

    return render_template('teacher/tasks.html', world=world, tasks=tasks)


@teacher_blueprint.route('/<world_id>/task/create')
@login_required
def create_task(world_id):
    world = World.query.filter_by(id=world_id, user_id=current_user.id).first()

    if not world:
        return redirect(url_for('game.home'))
    
    task = Task(world_id=world.id, index=world.question_index)

    world.question_index += 1

    db.session.add(task)
    db.session.commit()

    return redirect(f'/teacher/{world_id}/task/{task.id}/edit')


@teacher_blueprint.route('/<world_id>/task/<task_id>/edit')
@login_required
def edit_task(world_id, task_id):
    world = World.query.filter_by(id=world_id, user_id=current_user.id).first()

    if not world:
        return redirect(url_for('game.home'))
    
    task = Task.query.get(task_id)

    response = make_response(render_template('teacher/edit_task.html', world=world, task=task_serializer(task, True)))

    response.set_cookie('psk', get_key(current_user.id, world.id))
    response.set_cookie('task', str(task.id))

    return response


@teacher_blueprint.route('/<world_id>/task/<task_id>/delete')
@login_required
def delete_task(world_id, task_id):
    world = World.query.filter_by(id=world_id, user_id=current_user.id).first()

    if not world:
        return redirect(url_for('game.home'))
    
    world.question_index -= 1
    
    task = Task.query.get(task_id)

    for field in TaskField.query.filter_by(task_id=task.id).all():
        for option in TaskOption.query.filter_by(task_field_id=field.id).all():
            db.session.delete(option)

        if field.field_type == "image":
            path = os.path.join(os.getcwd(), 'media', 'tasks', field.content)

            if os.path.exists(path):
                os.remove(path)

        db.session.delete(field)

    db.session.delete(task)
    db.session.commit()

    return redirect(f"/teacher/{world_id}/tasks")
