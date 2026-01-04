from flask_sqlalchemy.pagination import SelectPagination

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
    comment = Comment()

    comment.author = author
    comment.post = post
    comment.content = content

    db.session.add(comment)
    db.session.commit()

    return comment
