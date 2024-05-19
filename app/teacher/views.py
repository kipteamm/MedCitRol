from flask_login import current_user, login_required

from flask import Blueprint, redirect, url_for, render_template, make_response, request

from app.utils.serializers import task_serializer, user_serializer, game_serializer, task_user_serializer
from app.utils.functions import get_key
from app.auth.models import UserWorlds, User
from app.game.models import World
from app.extensions import db

from .models import Task, TaskField, TaskOption, TaskUser

import os


teacher_blueprint = Blueprint('teacher', __name__, url_prefix="/teacher")


@teacher_blueprint.route('/<world_id>', methods=["GET", "POST"])
@login_required
def game(world_id):
    world = World.query.filter_by(id=world_id, user_id=current_user.id).first()

    if not world:
        return redirect(url_for('game.home'))
    
    if request.method == "POST":
        world.name = request.form['name']

        db.session.commit()

        return redirect(f'/teacher/{world_id}')

    return render_template('teacher/game.html', world=game_serializer(world), players=[user_serializer(User.query.get(user_world.user_id)) for user_world in UserWorlds.query.filter_by(world_id=world_id).all()])


@teacher_blueprint.route('/<world_id>/delete')
@login_required
def delete_game(world_id):
    world = World.query.filter_by(id=world_id, user_id=current_user.id).first()

    if not world:
        return redirect(url_for('game.home'))
    
    db.session.delete(world)
    db.session.commit()

    return redirect(url_for('game.home'))
    

@teacher_blueprint.route('/<world_id>/tasks')
@login_required
def tasks(world_id):
    world = World.query.filter_by(id=world_id, user_id=current_user.id).first()

    if not world:
        return redirect(url_for('game.home'))
    
    tasks = Task.query.filter_by(world_id=world.id).all()

    return render_template('teacher/tasks.html', world=game_serializer(world), tasks=[task_serializer(task) for task in tasks])


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

    if not task:
        return redirect(f'/teacher/{world_id}/tasks')

    response = make_response(render_template('teacher/edit_task.html', world=world, task=task_serializer(task, True)))

    response.set_cookie('psk', get_key(current_user.id, world.id))
    response.set_cookie('task', str(task.id))

    return response


@teacher_blueprint.route('/<world_id>/task/<task_id>/preview')
@login_required
def preview_task(world_id, task_id):
    world = World.query.filter_by(id=world_id, user_id=current_user.id).first()

    if not world:
        return redirect(url_for('game.home'))
    
    task = Task.query.get(task_id)

    if not task:
        return redirect(f'/teacher/{world_id}/tasks')

    return render_template('teacher/task_preview.html', world=world, task=task_serializer(task))


@teacher_blueprint.route('/<world_id>/task/<task_id>/info')
@login_required
def task_info(world_id, task_id):
    world = World.query.filter_by(id=world_id, user_id=current_user.id).first()

    if not world:
        return redirect(url_for('game.home'))
    
    task = Task.query.get(task_id)

    if not task:
        return redirect(f'/teacher/{world_id}/tasks')
    
    return render_template('teacher/task_info.html', world=game_serializer(world), task=task_serializer(task), task_info=[task_user_serializer(task_user) for task_user in TaskUser.query.filter_by(task_id=task_id).order_by(TaskUser.user_id, TaskUser.percentage.desc()).all()])


@teacher_blueprint.route('/<world_id>/task/<task_id>/delete')
@login_required
def delete_task(world_id, task_id):
    world = World.query.filter_by(id=world_id, user_id=current_user.id).first()

    if not world:
        return redirect(url_for('game.home'))
    
    world.question_index -= 1
    
    task = Task.query.get(task_id)

    for field in TaskField.query.filter_by(task_id=task.id).all():
        if field.field_type == "image":
            if TaskField.query.filter(TaskField.id != field.id, TaskField.content==field.content).first():
                db.session.delete(field)

                continue

            path = os.path.join(os.getcwd(), 'media', 'tasks', field.content)

            if os.path.exists(path):
                os.remove(path)

            db.session.delete(field)

            continue

        for option in TaskOption.query.filter_by(task_field_id=field.id).all():
            db.session.delete(option)

        db.session.delete(field)

    db.session.delete(task)
    db.session.commit()

    return redirect(f"/teacher/{world_id}/tasks")


@teacher_blueprint.route('/<world_id>/task/<task_id>/duplicate')
@login_required
def duplicate_task(world_id, task_id):
    world = World.query.filter_by(id=world_id, user_id=current_user.id).first()

    if not world:
        return redirect(url_for('game.home'))

    task = Task(world_id=world.id, index=world.question_index)

    db.session.add(task)
    db.session.commit()

    for old_field in TaskField.query.filter_by(task_id=task_id).all():
        task_field = TaskField(task_id=task.id, field_index=old_field.field_index, field_type=old_field.field_type, content=old_field.content)

        db.session.add(task_field)
        db.session.commit()

        for old_option in TaskOption.query.filter_by(task_field_id=old_field.id).all():
            task_option = TaskOption(task_field_id=task_field.id, field_type=old_option.field_type, content=old_option.content)

            db.session.add(task_option)
            db.session.commit()

    world.question_index += 1

    db.session.commit()

    return redirect(f"/teacher/{world_id}/task/{task.id}/edit")
