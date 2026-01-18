from typing import Optional

from flask_sqlalchemy.pagination import SelectPagination
from sqlalchemy import select

from db import Comment, Post, User, db
from .base import browse_element

def browse_comment(*args, **kwargs) -> SelectPagination:
    return browse_element(Comment, *args, **kwargs)

def create_comment(content: str, author: User, post: Post) -> Comment:
    """
    Creates and returns comment object.

    Args:
        content (str): Comment content
        author (User)
        post (Post)
    """
    content = content.strip()

    if len(content) == 0:
        return

    comment = Comment()

    comment.author = author
    comment.post = post
    comment.content = content

    db.session.add(comment)
    db.session.commit()

    return comment

def delete_comment(comment: Comment) -> None:
    db.session.delete(comment)
    db.session.commit()

def get_comment(comment_id: int) -> Optional[Comment]:
    comment = db.session.execute(
        select(Comment)
        .where(Comment.id == comment_id)
    ).scalars().first()

    return comment
