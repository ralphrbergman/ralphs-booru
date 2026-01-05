from hashlib import md5 as _md5
from pathlib import Path
from re import findall, sub, search
from shutil import copy
from typing import Optional

import ffmpeg
from flask_sqlalchemy.pagination import SelectPagination
from magic import from_file
from sqlalchemy import Select, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from db import Post, Tag, User, db
from .base import browse_element
from .tag import create_tag, get_tag
from .thumbnail import create_thumbnail

ATTR_PATTERN = r'[a-zA-Z0-9_]+:\S*'  # attr:value
CAPTION_PATTERN = r'"([^"]*)"'  # "hello world"
TAG_PATTERN = r'[a-zA-Z0-9-_]+'  # tag1 tag2 tag3

# What default term(s) shall be used when none are provided?
DEFAULT_TERMS = '-nsfw'

def browse_post(
    *args,
    terms: Optional[str] = DEFAULT_TERMS,
    **kwargs
) -> SelectPagination:
    """
    Creates and executes a select of posts by given criteria.

    Args:
        limit: How many posts per page to display
        page: Page number
        terms: Terms to search for if any
        sort_str: Sorting way

    Returns:
        SelectPagination
    """
    def apply_post_specific_queries(stmt: Select) -> None:
        nonlocal terms

        caption = None

        try:
            # Capture caption text from terms.
            caption = search(CAPTION_PATTERN, terms)[1]
            terms = sub(CAPTION_PATTERN, '', terms)
        except TypeError:
            pass

        # Capture attribute selectors.
        attrs = findall(ATTR_PATTERN, terms)
        terms = sub(ATTR_PATTERN, '', terms)

        # Get tags.
        tags = findall(TAG_PATTERN, terms)

        # Look for words in posts in unordered sequence.
        try:
            for word in caption.split():
                stmt = stmt.where(
                    Post.caption.like(f'%{word}%')
                )
        except AttributeError:
            pass

        # Apply attribute selectors.
        for attr in attrs:
            name, value = attr.split(':', 1)
            col = getattr(Post, name)

            if not len(value):
                # Look for posts that don't have the column set.
                where = or_(col == None, col == '')
            else:
                where = col == value

            stmt = stmt.where(where)

        # Apply tag selection.
        for tag in tags:
            if tag[0] != '-':
                where = Post.tags.any(Tag.name == tag)
            else:
                where = ~Post.tags.any(Tag.name == tag[1:])

            stmt = stmt.where(where)

        return stmt

    return browse_element(Post, apply_post_specific_queries, *args, **kwargs)

def count_all() -> int:
    return db.session.scalar(select(func.count(Post.id)))

def create_post(
    author: User,
    path: Path,
    directory: Optional[str] = None,
    op: Optional[str] = None,
    src: Optional[str] = None,
    caption: Optional[str] = None,
    tags: Optional[str] = None
) -> Post:
    post = Post()

    # Gather metadata about the post.
    dimensions = get_dimensions(path)
    ext = get_extension(path)
    md5 = get_hash(path)
    mime = get_mime(path)
    size = get_size(path)

    post.author_id = author.id
    post.op = op
    post.src = src

    post.caption = caption

    try:
        tag_objs = list()

        for tag_name in tags.split(' '):
            tag = get_tag(tag_name)

            if not tag:
                tag = create_tag(tag_name)

                if not tag:
                    continue

            post.tags.append(tag)
    except AttributeError as exc:
        pass

    post.directory = directory
    post.md5 = md5
    post.ext = ext

    post.mime = mime
    post.size = size

    try:
        post.height = dimensions[1]
        post.width = dimensions[0]
    except TypeError:
        pass

    post.path.parent.mkdir(parents = True, exist_ok = True)
    copy(path, post.path)
    path.unlink(missing_ok = True)

    for tag in tag_objs:
        db.session.add(tag)

    db.session.add(post)

    try:
        db.session.commit()

        thumbnail = create_thumbnail(post)

        try:
            thumbnail.post_id = post.id

            db.session.commit()
        except AttributeError as exc:
            # No thumbnail was made.
            pass
    except IntegrityError as exc:
        # Error likely of post that already exists.
        db.session.rollback()

        # Move back the file.
        copy(post.path, path)
        post.path.unlink(missing_ok = True)

        return

    return post

def delete_post(post: Post | int) -> None:
    """
    Deletes given post.

    Args:
        post (Post)
    """
    if isinstance(post, int):
        post = get_post(post)

    post.path.unlink(missing_ok = True)

    try:
        db.session.delete(post.thumbnail)
    except UnmappedInstanceError as exc:
        # Some posts may not have a thumbnail and it's alright.
        pass

    db.session.delete(post)
    db.session.commit()

def get_dimensions(path: Path) -> tuple[int, int]:
    try:
        probe_data = ffmpeg.probe(
            str(path),
            select_streams = 'v:0',
            show_entries = 'stream=width, height'
        )
    except ffmpeg.Error:
        # File isn't multimedia.
        return

    try:
        stream = probe_data['streams'][0]
    except (IndexError, KeyError):
        return

    return (stream['width'], stream['height'])

def get_extension(path: Path) -> str:
    return path.suffix[1:]

def get_hash(path: Path) -> str:
    with path.open('rb') as stream:
        return _md5(stream.read()).hexdigest()

def get_mime(path: Path) -> str:
    return from_file(str(path), mime = True)

def get_post(post_id: int) -> Optional[Post]:
    """
    Queries for a post by its ID.

    Args:
        post_id: The ID of a post you wish to see

    Returns:
        Post
    """
    return db.session.scalar(
        select(Post).where(
            Post.id.is_(post_id)
        )
    )

def get_size(path: Path) -> int:
    with path.open('rb') as stream:
        stream.seek(0, 2)

        return stream.tell()

def replace_post(post: Post, path: Path) -> Post:
    """
    Replaces given Post with new file.

    Args:
        post (Post): Post to replace
        path (Path): New file's Path object

    Returns:
        Post
    """
    original_id = post.id
    original_created = post.created
    original_modified = post.modified
    original_tags = post.tags

    new_post = create_post(
        author = post.author,
        path = path,
        op = post.op,
        src = post.src,
        caption = post.caption
    )

    if new_post:
        new_thumb = new_post.thumbnail

        delete_post(post)

        new_post.id = original_id
        new_post.created = original_created
        new_post.modified = original_modified
        new_post.tags = original_tags

        if new_thumb:
            # Tie post with its new thumbnail.
            new_thumb.post_id = new_post.id

        db.session.commit()

    return post
