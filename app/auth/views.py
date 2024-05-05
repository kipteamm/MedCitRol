from flask import Blueprint, render_template, request, flash, redirect, url_for

from flask_login import login_user, logout_user, current_user

from sqlalchemy import func

from app.auth.models import User
from app.game.models import AccessKey
from app.extensions import db


auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter(func.lower(User.email) == func.lower(email)).first(): # type: ignore
            flash('Email is already taken.', 'error')
            return render_template('auth/register.html')
        
        if len(password) > 128:
            flash(f'Your password is {len(password) - 128} characters too long.', 'error')
            return render_template('auth/register.html')

        if len(password) < 8:
            flash(f'Your password is {8 - len(password)} characters too short.', 'error')
            return render_template('auth/register.html')

        user = User(email, password)

        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        
        flash('Registration successful. Welcome!', 'success')
        
        return redirect(url_for('game.home'))
    
    return render_template('auth/register.html')


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.authenticate(email, password)
        
        if user:
            login_user(user)
            
            flash('Login successful. Welcome back!', 'success')
            
            return redirect(url_for('game.home'))
        else:
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html')

    return render_template('auth/login.html')


@auth_blueprint.route('/logout')
def logout():
    AccessKey.query.filter_by(user_id=current_user.id).delete()

    db.session.commit()

    logout_user()

    return redirect('/login')
