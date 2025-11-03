from os import getenv
from pathlib import Path
from typing import Optional

from flask import Blueprint, request, flash, redirect, render_template, send_from_directory, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from api import create_user, check_password, get_user, set_password
from api.decorators import anonymous_only, user_protect
from db import db
from form import LoginForm, PasswordForm, SignupForm, UserForm

AVATAR_PATH = Path(getenv('AVATAR_PATH'))

account_bp = Blueprint(
    name = 'Account',
    import_name = __name__
)

@account_bp.route('/avatar/<filename>')
def avatar_page(filename: str):
    return send_from_directory(AVATAR_PATH, filename)

@account_bp.route('/edit_profile', methods = ['GET', 'POST'])
@login_required
@user_protect
def edit_profile_page():
    form = UserForm()
    user = get_user(current_user.id)

    if request.method == 'GET':
        return render_template('edit_profile.html', form = form, user = user)
    else:
        if form.validate_on_submit():
            if check_password(user.password, form.pw.data):
                avatar: Optional[FileStorage] = form.avatar.data

                # Save & update user's avatar.
                if avatar:
                    filename = secure_filename(avatar.filename)
                    avatar.save(AVATAR_PATH / filename)

                    user.avatar_name = filename

                user.mail = form.email.data
                db.session.commit()

                flash('Updated profile successfully')
            else:
                flash('Invalid password provided')

            return redirect(url_for('Account.profile_page', user_id = user.id))
        else:
            for field in form.errors.values():
                for error in field:
                    flash(error)

            return redirect(url_for('Account.edit_profile_page'))

@account_bp.route('/edit_password', methods = ['GET', 'POST'])
@login_required
@user_protect
def edit_password_page():
    form = PasswordForm()
    user = get_user(current_user.id)

    if request.method == 'GET':
        return render_template('edit_password.html', form = form)
    else:
        if form.validate_on_submit():
            if check_password(user.password, form.pw.data):
                user.password = set_password(form.new_pw.data)
                db.session.commit()

                flash('Successfully changed password')
                return redirect(url_for('Account.edit_profile_page'))
            else:
                flash('Invalid password provided')
                return redirect(url_for('Account.profile_page', user_id = user.id))
        else:
            for field in form.errors.values():
                for error in field:
                    flash(error)

            return redirect(url_for('Account.edit_password_page'))

@account_bp.route('/login', methods = ['GET', 'POST'])
@anonymous_only
@user_protect
def login_page():
    form = LoginForm()

    if request.method == 'GET':
        return render_template('login.html', form = form)
    else:
        next_page = request.args.get('next')
        user = get_user(form.username.data)

        if not user:
            flash('Incorrect username')
            return redirect(url_for('Account.login_page', next = next_page))

        if form.validate_on_submit():
            if check_password(user.password, form.pw.data):
                login_user(user)

                flash(f'Welcome back, {user.name}')
                return redirect(next_page or url_for('Account.profile_page', user_id = user.id))
            else:
                flash('Incorrect password')
        else:
            for field in form.errors.values():
                for error in field:
                    flash(error)

        return redirect(url_for('Account.login_page', next = next_page))

@account_bp.route('/logout')
@login_required
def logout_page():
    logout_user()

    flash('Logged out')
    return redirect(url_for('Index.index_page'))

@account_bp.route('/profile/<int:user_id>')
def profile_page(user_id: int):
    user = get_user(user_id)
    # Return 10 posts the user has recently uploaded.
    posts = list(reversed(user.posts))[:10]

    return render_template(
        'profile.html',
        blur = request.args.get('blur', 'true') == 'true',
        posts = posts,
        user = user
    )

@account_bp.route('/signup', methods = ['GET', 'POST'])
@anonymous_only
@user_protect
def signup_page():
    form = SignupForm()

    if request.method == 'GET':
        return render_template('signup.html', form = form)
    else:
        if form.validate_on_submit():
            avatar: Optional[FileStorage] = form.avatar.data
            avatar_filename = None

            if avatar:
                avatar_filename = secure_filename(avatar.filename)
                avatar.save(AVATAR_PATH / avatar_filename)

            user = create_user(
                name = form.username.data,
                mail = form.email.data,
                password = form.pw.data,
                avatar = avatar_filename
            )

            if not user:
                return redirect(url_for('Account.signup_page'))

            login_user(user)

            flash(f'Welcome, {user.name}')
            return redirect(url_for('Account.profile_page', user_id = user.id))
        else:
            for field in form.errors.values():
                for error in field:
                    flash(error)

            return redirect(url_for('Account.signup_page'))
