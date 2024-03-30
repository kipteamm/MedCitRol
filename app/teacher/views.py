from flask_login import current_user, login_required

from flask import Blueprint, redirect, url_for, render_template

from app.game.models import World

from app.extensions import db

from .models import Task


teacher_blueprint = Blueprint('teacher', __name__, url_prefix="/teacher")


@teacher_blueprint.route('/<world_id>/game')
@login_required
def game(world_id):
    world = World.query.filter_by(id=world_id, user_id=current_user.id).first()

    if not world:
        return redirect(url_for('game.home'))

    return render_template('teacher/game.html', world=world.get_dict())


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

    return render_template('teacher/edit_task.html', world=world, task=task)
