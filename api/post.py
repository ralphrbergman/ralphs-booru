from hashlib import md5 as _md5
from pathlib import Path
from shutil import copy
from typing import Optional

import ffmpeg
from flask_sqlalchemy.pagination import Pagination
from magic import from_file
from sqlalchemy import func, select

from db import db, Post, User

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
    post.tags = tags

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

    db.session.add(post)
    db.session.commit()

    post.path.parent.mkdir(parents = True, exist_ok = True)
    copy(path, post.path)
    path.unlink(missing_ok = True)

    return post

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
    return from_file(path, mime = True)

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
