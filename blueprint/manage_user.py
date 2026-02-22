from logging import getLogger

from flask import Blueprint, request, abort, flash, redirect, render_template, url_for
from flask_babel import gettext
from flask_login import current_user, login_required

from api import browse_user, get_user, get_role_by_priority
from api.decorators import admin_only, moderator_only
from db import db
from form import ManageUserForm
from .utils import create_pagination_bar, flash_errors, log_user_activity

manage_user_bp = Blueprint(
    name = 'Manage User',
    import_name = __name__,
    url_prefix = '/manage_user'
)
logger = getLogger('app_logger')

@manage_user_bp.route('/list')
@login_required
@moderator_only
def user_list_page():
    return redirect(url_for('Root.Manage User.user_list_paged', page = 1))

@manage_user_bp.route('/list/<int:page>')
@login_required
@moderator_only
def user_list_paged(page: int):
    users = browse_user(page = page, terms = request.args.get('search'))
    bar = create_pagination_bar(
        page,
        users.pages,
        'Root.Manage User.user_list_page'
    )

    return render_template(
        'list_user.html',
        bar = bar,
        users = users,
        current_page = page,
    )

@manage_user_bp.route('/<int:user_id>', methods = ['GET', 'POST'])
@login_required
@admin_only
def manage_user_page(user_id: int):
    user = get_user(user_id)

    if not user:
        abort(404)

    form = ManageUserForm(
        obj = user,
        email = user.mail,
        username = user.name
    )

    if form.validate_on_submit():
        mail = form.email.data
        pw = None

        if len(form.pw.data) > 0:
            pw = form.pw.data

        priority = int(form.role.data)
        role = get_role_by_priority(priority)

        if not role:
            logger.error(f'Role with priority {priority} doesn\'t exist.')
            flash(
                gettext(
                    'Role with priority %(priority)s does not exist',
                    priority = priority
                )
            )
            role = user.role

        username = form.username.data

        if mail and mail != user.mail:
            log_user_activity(logger.info, f'changed e-mail of {user.name}')

        user.mail = mail

        if pw is not None:
            user.password = pw
            log_user_activity(logger.info, f'changed password of {user.name}')
        
        if (current_user.role.priority > user.role.priority and
            current_user.role.priority > role.priority):
            if user.role != role:
                user.role = role
                log_user_activity(logger.info, f'changed role of {user.name}')
        else:
            flash(
                gettext(
                    'Cannot manage the user on the same or above rank as you'
                )
            )
            log_user_activity(logger.warning, f'can\'t manage {user.name}')

            return redirect(
                url_for(
                    'Root.Manage User.manage_user_page',
                    user_id = user_id
                )
            )

        if user.name != username:
            log_user_activity(f'changed username of {user.name}')

        user.name = username

        db.session.commit()

        flash(
            gettext(
                'Updated user %(name)s successfully!',
                name = user.name
            )
        )
        log_user_activity(
            logger.info,
            f'updated user {user.name} successfully'
        )
    else:
        flash_errors(form)

    return render_template('manage_user.html', form = form, user = user)
