from logging import getLogger
from typing import Optional, TypeVar

from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import Select, and_, or_, select

from db import db, Post, Tag
from .base import browse_element

T = TypeVar('T')

logger = getLogger('app_logger')

def add_tags(tags_str: str) -> list[Tag]:
    tags = decode_tags(tags_str)

    return tags

def browse_tag(*args, **kwargs) -> 'Pagination[Tag]':
    """
    Paginates tags by criteria.

    Args:
        direction (str, optional): Sorting direction, asc for ascending
        and desc for descending
        limit (int): Amount of tags per page
        page (int): Page
        sort (str): Tag's column to sort by
        terms (str): Tag name to search for
    """
    def tag_select(stmt: Select[T]) -> Select[T]:
        terms: str = kwargs.get('terms')
        if not terms:   return stmt

        n_cond = set()  # Store excluding tags
        p_cond = set()  # Store including tags

        for word in terms.split():
            if word.startswith('-'):
                n_cond.add(Tag.name != word[1:])
            else:
                p_cond.add(Tag.name.icontains(word))
                p_cond.add(Tag.name == word)

            logger.debug(f'Searching tag: {word}')

        if p_cond:
            stmt = stmt.where(or_(*p_cond))

        if n_cond:
            stmt = stmt.where(and_(*n_cond))

        return stmt

    return browse_element(Tag, tag_select, *args, **kwargs)

def create_tag(name: str, posts: Optional[list[Post]] = None) -> Tag | None:
    """
    Creates and returns tag object.

    Args:
        name: Tag's name
        posts: Optional for adding tag to posts
    """
    tag = Tag()
    db.session.add(tag)

    try:
        tag.name = name
    except ValueError:
        # Name of tag is purely invalid characters.
        db.session.expunge(tag)
        return None

    try:
        for post in posts:
            post.tags.append(tag)
    except TypeError as exception:
        pass

    logger.info(f'Created tag: {name}')
    return tag

def delete_tag(tag: Tag) -> None:
    """
    Deletes given tag.
    """
    db.session.delete(tag)
    logger.info(f'Deleting tag: {tag.name}')

def decode_tags(tags_str: str) -> list[Tag]:
    tags_str = tags_str.lower()

    tags = []
    tag_names = set()

    for tag_name in tags_str.split():
        if tag_name in tag_names: continue

        tag = get_tag(tag_name) or create_tag(tag_name)

        tags.append(tag)
        tag_names.add(tag_name)

    return tags

def encode_tags(tags: list[Tag]) -> str:
    tags.sort(key = lambda tag: tag.name.lower())
    tags_str = ' '.join([ tag.name for tag in tags ])

    return tags_str

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
