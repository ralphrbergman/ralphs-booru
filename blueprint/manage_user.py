from flask import Blueprint, request, flash, redirect, render_template, url_for
from flask_babel import gettext
from flask_login import current_user

from api import browse_user, get_user
from api.decorators import moderator_only
from db import db, RoleEnum
from form import ManageUserForm
from .utils import create_pagination_bar

manage_user_bp = Blueprint(
    name = 'Manage User',
    import_name = __name__,
    url_prefix = '/manage_user'
)

@manage_user_bp.route('/list')
@moderator_only
def user_list_page():
    page = request.args.get('page', default = 1, type = int)

    users = browse_user(page = page)
    bar = create_pagination_bar(page, users.pages, 'Root.Manage User.user_list_page')

    return render_template(
        'list_user.html',
        bar = bar,
        users = users,
        current_page = page,
        enum = RoleEnum
    )

@manage_user_bp.route('/<int:user_id>', methods = ['GET', 'POST'])
@moderator_only
def manage_user_page(user_id: int):
    user = get_user(user_id)
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

        role = int(form.role.data)
        username = form.username.data

        user.mail = mail
        if pw is not None:
            user.password = pw
        
        if current_user.role >= RoleEnum(role):
            user.role = role
        else:
            flash(gettext('Cannot grant a role that you are below of'))
            return redirect(url_for('Root.Manage User.manage_user_page', user_id = user_id))

        user.name = username

        db.session.commit()
        flash(gettext('Updated user %(name)s successfully!', name = user.name))

    return render_template('manage_user.html', form = form, user = user)
