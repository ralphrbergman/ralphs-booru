from flask import Blueprint, request, flash, redirect, render_template, url_for
from flask_login import login_user, logout_user

from api import create_user, check_password, get_user
from forms import LoginForm, SignupForm

account_bp = Blueprint(
    name = 'Account',
    import_name = __name__
)

@account_bp.route('/profile/<int:user_id>')
def profile_page(user_id: int):
    return render_template('profile.html', user = get_user(user_id))

@account_bp.route('/login', methods = ['GET', 'POST'])
def login_page():
    form = LoginForm()

    if request.method == 'GET':
        return render_template('login.html', form = form)
    else:
        user = get_user(form.username.data)

        if not user:
            flash('Incorrect username')
            return redirect(url_for('Account.login_page'))

        if check_password(user.password, form.pw.data):
            login_user(user)

            flash(f'Welcome back, {user.name}')
            return redirect(url_for('Account.profile_page', user_id = user.id))
        else:
            flash('Incorrect password')
            return redirect(url_for('Account.login_page'))

@account_bp.route('/logout')
def logout_page():
    logout_user()

    flash('Logged out')
    return redirect(url_for('Index.index_page'))

@account_bp.route('/signup', methods = ['GET', 'POST'])
def signup_page():
    form = SignupForm()

    if request.method == 'GET':
        return render_template('signup.html', form = form)
    else:
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
