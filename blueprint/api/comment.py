from apiflask import APIBlueprint
from flask import redirect, url_for
from flask_login import current_user, login_required

from api import create_comment, get_post
from db.schemas import CommentIn, CommentOut

comment_bp = APIBlueprint(
    name = 'Comment API',
    import_name = __name__,
    url_prefix = '/comment'
)

@comment_bp.post('')
@login_required
@comment_bp.input(CommentIn, arg_name = 'data', location = 'form')
@comment_bp.output(CommentOut)
def comment_route(data: CommentIn):
    post = get_post(data['post_id'])

    comment = create_comment(
        content = data['content'],
        author = current_user,
        post = post
    )

    if data['is_ui']:
        return redirect(url_for('Post.view_page', post_id = post.id))
    else:
        return comment
