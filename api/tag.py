from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError

from db import db, Post, Tag

def create_tag(name: str, posts: Optional[list[Post]] = None) -> Tag:
    """
    Creates and returns tag object.

    Args:
        name (str): Tag's name
        posts (list): Optional for adding tag to posts

    Returns:
        Tag
    """
    tag = Tag()
    db.session.add(tag)

    tag.name = name

    try:
        for post in posts:
            post.tags.append(tag)
    except TypeError as exc:
        pass

    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        return

    return tag

def get_tag(id: str | int) -> Optional[Tag]:
    """
    Queries for a tag and returns.

    Args:
        name (str | int)

    Returns:
        Tag
    """
    return db.session.scalar(
        select(Tag).where(
            or_(
                Tag.id.is_(id),
                Tag.name.is_(id)
            )
        )
    )
