from typing import Optional, TypeVar

from flask_sqlalchemy.pagination import SelectPagination
from sqlalchemy import Select, and_, or_, select

from db import Comment, Post, User, db
from .base import browse_element

T = TypeVar('T')

def browse_comment(*args, **kwargs) -> SelectPagination:
    """
    Paginates comments by criteria.

    Args:
        direction (str, optional): Sorting direction, asc for ascending
        and desc for descending
        limit (int): Amount of comments per page
        page (int): Page
        sort (str): Comment's column to sort by
        terms (str): Words to search
    """
    def comment_select(stmt: Select[T]) -> Select[T]:
        terms: str = kwargs.get('terms')
        if not terms:   return stmt

        conditions = set()

        for word in terms.split():
            conditions.add(Comment.content == word)
            conditions.add(Comment.content.icontains(word))

        return stmt.where(or_(*conditions))

    return browse_element(Comment, comment_select, *args, **kwargs)

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

    # Find already existing comment with the same content to prevent spamming.
    comment = db.session.scalars(
        select(Comment)
        .where(and_(Comment.content == content, Comment.author == author))
    ).first()

    if comment:
        return

    comment = Comment()

    comment.author = author
    comment.post = post
    comment.content = content

    db.session.add(comment)

    return comment

def delete_comment(comment: Comment) -> None:
    """
    Mark given comment deleted.
    """
    db.session.delete(comment)

def get_comment(comment_id: int) -> Optional[Comment]:
    """
    Get comment from ID.

    Args:
        comment_id: Comment's unique ID
    """
    comment = db.session.execute(
        select(Comment)
        .where(Comment.id == comment_id)
    ).scalars().first()

    return comment
