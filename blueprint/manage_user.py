from flask import Blueprint, request, flash, render_template

from api import browse_user, get_user, set_password
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
    bar = create_pagination_bar(page, users.pages, 'Manage User.user_list_page')

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
            pw = set_password(form.pw.data)

        role = form.role.data
        username = form.username.data

        user.mail = mail
        if pw is not None:
            user.password = pw
        user.role = role
        user.name = username

        db.session.commit()
        flash(f'Updated user {user.name} successfully!')

    return render_template('manage_user.html', form = form, user = user)
