from functools import wraps

from flask import Blueprint, request, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from api import create_user, check_password, get_user, set_password
from db import db
from form import LoginForm, PasswordForm, SignupForm, UserForm

def anonymous_only(callback):
    """
    Restricts view for anonymous users only.

    Args:
        callback: Route to restrict
    """
    @wraps(callback)
    def wrapper(*args, **kwargs):
        if current_user.is_anonymous:
            return callback(*args, **kwargs)
        else:
            return abort(401)

    return wrapper

account_bp = Blueprint(
    name = 'Account',
    import_name = __name__
)

@account_bp.route('/edit_profile', methods = ['GET', 'POST'])
@login_required
def edit_profile_page():
    form = UserForm()
    user = get_user(current_user.id)

    if request.method == 'GET':
        return render_template('edit_profile.html', form = form, user = user)
    else:
        if form.validate_on_submit():
            if check_password(user.password, form.pw.data):
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
def login_page():
    form = LoginForm()

    if request.method == 'GET':
        return render_template('login.html', form = form)
    else:
        user = get_user(form.username.data)

        if not user:
            flash('Incorrect username')
            return redirect(url_for('Account.login_page'))

        if form.validate_on_submit():
            if check_password(user.password, form.pw.data):
                login_user(user)

                flash(f'Welcome back, {user.name}')
                return redirect(url_for('Account.profile_page', user_id = user.id))
            else:
                flash('Incorrect password')
        else:
            for field in form.errors.values():
                for error in field:
                    flash(error)

        return redirect(url_for('Account.login_page'))

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

    return render_template('profile.html', posts = posts, user = user)

@account_bp.route('/signup', methods = ['GET', 'POST'])
@anonymous_only
def signup_page():
    form = SignupForm()

    if request.method == 'GET':
        return render_template('signup.html', form = form)
    else:
        if form.validate_on_submit():
            user = create_user(
                name = form.username.data,
                mail = form.email.data,
                password = form.pw.data
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
