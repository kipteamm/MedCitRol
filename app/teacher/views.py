from flask_login import current_user, login_required

from flask import Blueprint, redirect, url_for, render_template, request

from app.utils.serializers import task_serializer, world_task_preview_serializer, user_serializer, game_serializer, task_user_serializer
from app.auth.models import UserWorlds, User
from app.game.models import World
from app.extensions import db

from .models import Task, WorldTask, TaskUser


teacher_blueprint = Blueprint('teacher', __name__, url_prefix="/teacher")


@teacher_blueprint.route('/<world_id>', methods=["GET", "POST"])
@login_required
def game(world_id):
    world = World.query.filter_by(id=world_id, user_id=current_user.id).first()

    if not world:
        return redirect(url_for('home.games'))
    
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
        return redirect(url_for('home.games'))
    
    db.session.delete(world)
    db.session.commit()

    return redirect(url_for('home.games'))
    

@teacher_blueprint.route('/<world_id>/tasks')
@login_required
def tasks(world_id):
    world = World.query.filter_by(id=world_id, user_id=current_user.id).first()

    if not world:
        return redirect(url_for('home.games'))
    
    tasks = WorldTask.query.filter_by(world_id=world.id).all()

    return render_template('teacher/tasks.html', world=game_serializer(world), tasks=[world_task_preview_serializer(task) for task in tasks])


@teacher_blueprint.route('/task/<task_id>/info')
@login_required
def task_info(task_id):
    world_query = request.args.get('world')

    world_task = WorldTask.query.filter_by(world_id=world_query, task_id=task_id).first()

    if not world_task:
        return redirect(url_for('home.games'))
    
    task = Task.query.get(task_id)

    if task.user_id != current_user.id:
        return redirect(f'/tasks')
    
    return render_template('teacher/task_info.html', task=task_serializer(task), task_info=[task_user_serializer(task_user) for task_user in TaskUser.query.filter_by(task_id=task_id).order_by(TaskUser.user_id, TaskUser.percentage.desc()).all()])
