from hashlib import md5 as _md5
from pathlib import Path
from shutil import copy
from typing import Optional

import ffmpeg
from magic import from_file
from sqlalchemy import func, select
from sqlalchemy.orm.exc import UnmappedInstanceError

from db import Post, User, db
from .tag import create_tag, get_tag
from .thumbnail import create_thumbnail

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

                    tag_objs.append(tag)

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
    db.session.commit()

    thumbnail = create_thumbnail(post)
    try:
        thumbnail.post_id = post.id

        db.session.commit()
    except AttributeError as exc:
        # No thumbnail was made.
        pass

    return post

def delete_post(post: Post) -> None:
    """
    Deletes given post.

    Args:
        post (Post)
    """
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
