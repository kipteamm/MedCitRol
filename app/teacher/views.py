from flask_login import current_user, login_required

from flask import Blueprint, redirect, url_for, render_template, make_response, request

from app.utils.serializers import task_serializer, task_preview_serializer, user_serializer, game_serializer, task_user_serializer
from app.utils.functions import get_key
from app.auth.models import UserWorlds, User
from app.game.models import World
from app.extensions import db

from .models import Task, WorldTask, TaskField, TaskOption, TaskUser

import os


teacher_blueprint = Blueprint('teacher', __name__, url_prefix="/teacher")


@teacher_blueprint.route('/tasks')
@login_required
def teacher_tasks():
    return render_template('teacher/tasks.html', tasks=[task_serializer(task) for task in Task.query.filter_by(user_id=current_user.id).all()], world=None)


@teacher_blueprint.route('/task/create')
@login_required
def create_task():
    task = Task(user_id=current_user.id)

    db.session.add(task)
    db.session.commit()

    world_query = request.args.get('world')

    world = World.query.get(world_query)

    if world:
        world_task = WorldTask(world_id=world.id, task_id=task.id, index=world.task_index)

        world.task_inde += 1

        db.session.add(world_task)
        db.session.commit()

        world_query = f'?world={world.id}'

    return redirect(f'/teacher/task/{task.id}/edit{world_query}')


@teacher_blueprint.route('/task/<task_id>/edit')
@login_required
def edit_task(task_id):
    task = Task.query.get(task_id)

    if not task or task.user_id != current_user.id:
        return redirect(f"/teacher/tasks")

    response = make_response(render_template('teacher/edit_task.html', task=task_serializer(task, True)))

    response.set_cookie('token', current_user.token)
    response.set_cookie('task', task.id)

    return response


@teacher_blueprint.route('/task/<task_id>/preview')
@login_required
def preview_task(task_id):
    task = Task.query.get(task_id)

    world_query = request.args.get('world')

    if not task or task.user_id != current_user.id:
        return redirect(f'/teacher/tasks')
    
    if world_query and not WorldTask.query.filter_by(task_id=task.id, world_id=world_query).first():
        return redirect(f'/teacher/task/{task.id}/edit{f"?world={world_query}" if world_query else ""}')

    return render_template('teacher/task_preview.html', task=task_serializer(task))


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

    if tasks:
        for task in tasks:
            if task.user_id != None:
                continue

            task.user_id = current_user.id
            task.world_id = None
            task.index = None
            
            world_task = WorldTask(task_id=task.id, world_id=world.id, index=task.index)

            db.session.add(world_task)
            db.session.commit()

    return render_template('teacher/tasks.html', world=game_serializer(world), tasks=[task_preview_serializer(task) for task in tasks])


@teacher_blueprint.route('/task/<task_id>/info')
@login_required
def task_info(task_id):
    world_query = request.args.get('world')

    world_task = WorldTask.query.filter_by(world_id=world_query, task_id=task_id).first()

    if not world_task:
        return redirect(url_for('game.home'))
    
    task = Task.query.get(task_id)

    if task.user_id != current_user.id:
        return redirect(f'/teacher/tasks')
    
    return render_template('teacher/task_info.html', task=task_serializer(task), task_info=[task_user_serializer(task_user) for task_user in TaskUser.query.filter_by(task_id=task_id).order_by(TaskUser.user_id, TaskUser.percentage.desc()).all()])
