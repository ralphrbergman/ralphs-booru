from flask import Blueprint, request, render_template

from api import browse_comment, count_all_posts
from .utils import create_pagination_bar

comment_bp = Blueprint(
    name = 'Comment',
    import_name = __name__
)

@comment_bp.route('/comments')
def comment_page():
    page = request.args.get('page', default = 1, type = int)

    comments = browse_comment(page = page)
    bar = create_pagination_bar(page, comments.pages, 'Root.Comment.comment_page')

    return render_template(
        'comment.html',
        bar = bar,
        comments = comments,
        current_page = page,
        post_count = count_all_posts()
    )
