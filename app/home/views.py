from flask import Blueprint, render_template, request, redirect, url_for, make_response

from flask_login import login_required, current_user

from app.utils.serializers import task_serializer
from app.teacher.models import Task, WorldTask
from app.auth.models import UserWorlds
from app.game.models import World
from app.extensions import db


home_blueprint = Blueprint('home', __name__)


@home_blueprint.route('/games')
@login_required
def games():
    world_id = request.args.get('game')

    if UserWorlds.query.filter_by(world_id=world_id).first():
        return redirect(f'/game/{world_id}')

    worlds = []

    for world in current_user.worlds:
        worlds.append({
            'id': world.id,
            'user_id': world.user_id,
            'name' : world.name,
            'code': world.code
        })

    return render_template("home/games.html", worlds=worlds)


@home_blueprint.route('/invite/<invite>')
@login_required
def invite(invite):
    world = World.query.filter_by(code=invite).first()

    if not world:
        return redirect(url_for('home.games'))
    
    user_world = UserWorlds.query.filter_by(user_id=current_user.id, world_id=world.id).first()

    if user_world:
        return redirect(f'/game/{user_world.world_id}')
    
    current_user.worlds.append(world)

    db.session.commit()

    return redirect(f'/game/{world.id}')


@home_blueprint.route('/game/create/<psw>')
@login_required
def create_game(psw):
    if psw != "jogHq2Hndb":
        return redirect(url_for('home.games'))

    world = World(user_id=current_user.id)

    db.session.add(world)

    current_user.worlds.append(world)

    db.session.commit()

    return redirect(f'/teacher/{world.id}')


@home_blueprint.route('/tasks')
@login_required
def teacher_tasks():
    return render_template('home/tasks.html', tasks=[task_serializer(task) for task in Task.query.filter_by(user_id=current_user.id).all()], world=None)


@home_blueprint.route('/task/create')
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

    return redirect(f'/task/{task.id}/edit{world_query}')


@home_blueprint.route('/task/<task_id>/edit')
@login_required
def edit_task(task_id):
    task = Task.query.get(task_id)

    if not task or task.user_id != current_user.id:
        return redirect(f"/tasks")

    response = make_response(render_template('teacher/edit_task.html', task=task_serializer(task, True)))

    response.set_cookie('task', task.id)

    return response


@home_blueprint.route('/task/<task_id>/preview')
@login_required
def preview_task(task_id):
    task = Task.query.get(task_id)

    world_query = request.args.get('world')

    if not task or task.user_id != current_user.id:
        return redirect(f'/tasks')
    
    if world_query and not WorldTask.query.filter_by(task_id=task.id, world_id=world_query).first():
        return redirect(f'/task/{task.id}/edit{f"?world={world_query}" if world_query else ""}')

    return render_template('teacher/task_preview.html', task=task_serializer(task))