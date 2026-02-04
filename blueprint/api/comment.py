from os import getenv

from apiflask import APIBlueprint, abort
from flask_login import current_user

from api import create_comment, delete_comment, get_comment, get_post
from api.decorators import owner_only, post_protect, perm_required
from api_auth import auth
from db import Comment, db
from db.schemas import CommentIn, CommentOut

COMMENT_LEVEL = int(getenv('COMMENT_LEVEL'))

comment_bp = APIBlueprint(
    name = 'Comment API',
    import_name = __name__,
    url_prefix = '/comment'
)

@comment_bp.get('/<int:comment_id>')
@comment_bp.output(CommentOut)
def obtain_comment(comment_id: int):
    """
    Find comment by its unique identifier.
    """
    return get_comment(comment_id)

@comment_bp.delete('/<int:comment_id>')
@comment_bp.output({}, status_code = 204)
@comment_bp.auth_required(auth)
@owner_only(Comment)
def remove_comment(comment_id: int, comment: Comment):
    """
    Delete specific comment.
    """
    if not comment:
        abort(404, message = 'Comment not found.')

    delete_comment(comment)
    db.session.commit()

    return {}

@comment_bp.patch('/<int:comment_id>')
@comment_bp.input(CommentIn, arg_name = 'data')
@comment_bp.output(CommentOut)
@comment_bp.auth_required(auth)
@post_protect
@owner_only(Comment)
def update_comment(comment_id: int, data: CommentIn):
    """
    Update specific comment. Only the owner of the comment can update.
    """
    comment = get_comment(comment_id)
    post = get_post(data['post_id'])

    if not post:
        abort(400, message = 'Post not found.')

    if not comment:
        abort(404, message = 'Comment not found.')

    for key, value in data.items():
        setattr(comment, key, value)

    db.session.commit()
    return comment

@comment_bp.post('')
@comment_bp.input(CommentIn, arg_name = 'data')
@comment_bp.output(CommentOut)
@comment_bp.auth_required(auth)
@post_protect
@perm_required('post:comment')
def upload_comment(data: CommentIn):
    """
    Post a comment.
    """
    post = get_post(data['post_id'])

    if not post:
        abort(404, message = 'Post not found.')

    comment = create_comment(data['content'], current_user, post)
    db.session.commit()

    return comment
