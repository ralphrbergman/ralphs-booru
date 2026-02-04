from typing import Optional

from flask_sqlalchemy.pagination import SelectPagination
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError

from db import db, Post, Tag
from .base import browse_element

def add_tags(tag_list: list[str]) -> list[Tag]:
    """
    Creates a list of tags and returns created instances.

    Args:
        tag_list: List of tag names
    """
    new_tags = list()
    # This is used to ignore tags that have been already added.
    tag_names = set()

    for tag_name in tag_list:
        if len(tag_name) == 0 or tag_name in tag_names:
            break

        tag = get_tag(tag_name)

        if not tag:
            tag = create_tag(tag_name)

        new_tags.append(tag)
        tag_names.add(tag_name)

    return new_tags

def browse_tag(*args, **kwargs) -> SelectPagination:
    """
    Creates and executes a select of tags by criteria.
    """
    return browse_element(Tag, *args, **kwargs)

def create_tag(name: str, posts: Optional[list[Post]] = None) -> Tag:
    """
    Creates and returns tag object.

    Args:
        name: Tag's name
        posts: Optional for adding tag to posts
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

def delete_tag(tag: Tag) -> None:
    """
    Deletes given tag.
    """
    db.session.delete(tag)
    db.session.commit()

def get_tag(id: str | int) -> Optional[Tag]:
    """
    Queries for a tag and returns.

    Args:
        id: Tag's name or its ID
    """
    return db.session.scalar(
        select(Tag).where(
            or_(
                Tag.id.is_(id),
                Tag.name.is_(id)
            )
        )
    )
