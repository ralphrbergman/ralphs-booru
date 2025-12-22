from typing import Literal, Optional

from flask_sqlalchemy.pagination import SelectPagination
from sqlalchemy import select

from db import Comment, Post, User, db

DEFAULT_LIMIT = 20
DEFAULT_SORT = 'desc'
LIMIT_THRESHOLD = 100

def browse_comment(
    limit: Optional[int] = DEFAULT_LIMIT,
    page: Optional[int] = 1,
    sort_str: Optional[Literal['asc', 'desc']] = DEFAULT_SORT
) -> SelectPagination:
    if limit and limit > LIMIT_THRESHOLD:
        limit = LIMIT_THRESHOLD

    stmt = select(Comment).order_by(
        getattr(Comment.id, sort_str)()
    )

    comments = db.paginate(
        stmt,
        page = page,
        per_page = limit
    )

    return comments

def create_comment(content: str, author: User, post: Post) -> Comment:
    """
    Creates and returns comment object.

    Args:
        content (str): Comment content
        author (User)
        post (Post)
    """
    comment = Comment()

    comment.author = author
    comment.post = post
    comment.content = content

    db.session.add(comment)
    db.session.commit()

    return comment
