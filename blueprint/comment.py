from flask import Blueprint, request, redirect, render_template, url_for

from api import browse_comment, count_all_posts
from .utils import create_pagination_bar

comment_bp = Blueprint(
    name = 'Comment',
    import_name = __name__,
    url_prefix = '/comments'
)

@comment_bp.route('')
def comment_page():
    return redirect(url_for('Root.Comment.comment_paged', page = 1))

@comment_bp.route('/<int:page>')
def comment_paged(page: int):
    comments = browse_comment(
        page = page,
        terms = request.args.get('search')
    )

    bar = create_pagination_bar(
        page,
        comments.pages,
        'Root.Comment.comment_page'
    )

    return render_template(
        'comment.html',
        bar = bar,
        comments = comments,
        current_page = page,
        post_count = count_all_posts()
    )
