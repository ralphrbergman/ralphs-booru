from logging import getLogger
from os import getenv
from pathlib import Path
from typing import Optional

from flask import (
    Blueprint,
    request,
    abort,
    flash,
    redirect,
    render_template,
    send_from_directory,
    url_for
)
from flask_babel import gettext
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from api import create_user, get_user, get_user_by_username
from api.decorators import anonymous_only, user_protect
from db import db
from form import LoginForm, PasswordForm, SignupForm, UserForm
from .utils import flash_errors, log_anon_activity, log_user_activity

AVATAR_PATH = Path(getenv('AVATAR_PATH'))

account_bp = Blueprint(
    name = 'Account',
    import_name = __name__
)
logger = getLogger('app_logger')

@account_bp.route('/avatar/<filename>')
def avatar_page(filename: str):
    return send_from_directory(AVATAR_PATH, filename)

@account_bp.route('/edit_profile', methods = ['GET', 'POST'])
@login_required
@user_protect
def edit_profile_page():
    form = UserForm()

    if form.validate_on_submit():
        if current_user.check_password(form.pw.data):
            avatar: Optional[FileStorage] = form.avatar.data

            # Save & update current_user's avatar.
            if avatar:
                filename = secure_filename(avatar.filename)
                avatar.save(AVATAR_PATH / filename)

                current_user.avatar_name = filename
                log_user_activity(logger.debug, 'changed their avatar.')

            # E-mail.
            if current_user.mail != form.email.data:
                log_user_activity(logger.debug, 'updated their e-mail address')

            current_user.mail = form.email.data

            db.session.commit()
            log_anon_activity(logger.debug, 'updated their profile')

            flash(gettext('Updated profile successfully'))
        else:
            log_user_activity(logger.warning, 'submitted an invalid password')

            flash(gettext('Invalid password provided'))

        return redirect(
            url_for(
                'Root.Account.profile_page',
                user_id = current_user.id
                )
            )

    flash_errors(form)

    return render_template(
        'edit_profile.html',
        form = form,
        user = current_user
    )

@account_bp.route('/edit_password', methods = ['GET', 'POST'])
@login_required
@user_protect
def edit_password_page():
    form = PasswordForm()

    if form.validate_on_submit():
        if current_user.check_password(form.pw.data):
            current_user.password = form.new_pw.data
            db.session.commit()

            log_user_activity(logger.info, 'changed their password')

            flash(gettext('Successfully changed password'))
            return redirect(url_for('Root.Account.edit_profile_page'))
        else:
            log_user_activity(logger.warning, 'submitted an invalid password')

            flash(gettext('Invalid password provided'))
            return redirect(
                url_for(
                    'Root.Account.profile_page',
                    user_id = current_user.id
                )
            )

    flash_errors(form)

    return render_template('edit_password.html', form = form)

@account_bp.route('/login', methods = ['GET', 'POST'])
@anonymous_only
@user_protect
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        next_page = request.args.get('next')
        current_user = get_user_by_username(form.username.data)

        if not current_user:
            log_anon_activity(logger.warning, 'inputted incorrect username.')

            flash(gettext('Incorrect username'))

            return redirect(
                url_for(
                    'Root.Account.login_page',
                    next = next_page
                )
            )

        if current_user.check_password(form.pw.data):
            login_user(current_user, remember = form.remember.data)

            log_user_activity(logger.debug, 'logged in successfully')

            flash(gettext('Welcome back, %(name)s', name = current_user.name))

            return redirect(
                next_page or url_for(
                    'Root.Account.profile_page',
                    user_id = current_user.id
                )
            )
        else:
            log_user_activity(logger.warning, 'submitted an invalid password')

            flash(gettext('Incorrect password'))

    flash_errors(form)

    return render_template('login.html', form = form)

@account_bp.route('/logout')
@login_required
def logout_page():
    logout_user()

    log_user_activity(logger.debug, 'logged out successfully.')

    flash(gettext('Logged out'))

    return redirect(url_for('Root.Index.index_page'))

@account_bp.route('/profile/<int:user_id>')
def profile_page(user_id: int):
    user = get_user(user_id)

    if not user:
        return abort(404)

    return render_template(
        'profile.html',
        blur = request.args.get('blur', 'true') == 'true',
        posts = user.recent_posts,
        user = user
    )

@account_bp.route('/signup', methods = ['GET', 'POST'])
@anonymous_only
@user_protect
def signup_page():
    form = SignupForm()

    if form.validate_on_submit():
        avatar: Optional[FileStorage] = form.avatar.data
        avatar_filename = None

        if avatar:
            avatar_filename = secure_filename(avatar.filename)
            avatar.save(AVATAR_PATH / avatar_filename)

            log_anon_activity(logger.debug, 'successfully uploaded their own avatar.')

        current_user = create_user(
            name = form.username.data,
            mail = form.email.data,
            password = form.pw.data,
            avatar = avatar_filename
        )

        try:
            db.session.commit()
        except IntegrityError as exception:
            logger.error(
                f'failed to create user: {current_user.name=}'\
                f'& {'*' * len(current_user.mail)}')

            current_user = None

        if not current_user:
            log_anon_activity(
                logger.error,
                f'failed to create user {current_user.name}'
            )

            flash(gettext('Failed to create your profile.'))
            return redirect(url_for('Root.Account.signup_page'))

        login_user(current_user, remember = True)

        log_user_activity(logger.debug, 'successfully made their account')

        flash(gettext('Welcome, %(name)s', name = current_user.name))
        return redirect(
            url_for(
                'Root.Account.profile_page',
                user_id = current_user.id
            )
        )

    flash_errors(form)

    return render_template('signup.html', form = form)
