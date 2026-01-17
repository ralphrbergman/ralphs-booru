from apiflask import APIBlueprint, abort
from flask_login import current_user

from api import get_user, get_user_by_username
from api.decorators import key_required
from db.schemas import UserOut

user_bp = APIBlueprint(
    name = 'User API',
    import_name = __name__,
    url_prefix = '/user'
)

@user_bp.get('/<int:user_id>')
@user_bp.output(UserOut)
def obtain_user(user_id: int):
    user = get_user(user_id)

    if not user:
        abort(404, message = 'No user found.')

    return user

@user_bp.get('/username/<username>')
@user_bp.output(UserOut)
def obtain_user_by_username(username: str):
    user = get_user_by_username(username)

    if not user:
        abort(404, message = 'No user found.')

    return user

@user_bp.get('/authenticated')
@user_bp.output(UserOut)
@key_required
def obtain_authenticated_user():
    return current_user
