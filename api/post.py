from hashlib import md5 as _md5
from os import getenv
from pathlib import Path
from re import findall, sub, search
from shutil import copy
from typing import Optional, TypeVar

import ffmpeg
from flask_sqlalchemy.pagination import SelectPagination
from magic import from_file
from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm.exc import UnmappedInstanceError
from werkzeug.datastructures import FileStorage

from db import Post, Tag, User, db
from .base import browse_element
from .removed import create_log
from .tag import create_tag, get_tag
from .thumbnail import create_thumbnail

NONALPHA = r'[^a-zA-Z0-9.]'
ATTR_PATTERN = r'\b\w+:[<>]?\S*'  # attr:value, attr: , attr:<value, attr:>value
CAPTION_PATTERN = r'"([^"]*)"'  # "hello world"
TAG_PATTERN = r'[a-zA-Z0-9-_()]+'  # tag1 tag2 tag3

MIME_MAP = {
    'gif': 'image/gif',
    'mjpeg': 'image/jpeg',
    'mp3': 'audio/mpeg',
    'mpeg': 'audio/mpeg',
    'mp4': 'video/mp4',
    'image2': 'image/png',
    'png': 'image/png',
    'png_pipe': 'image/png',
    'webm': 'video/webm',
    'webp': 'image/webp',
    'webp_pipe': 'image/webp'
}

CONTENT_PATH = Path(getenv('CONTENT_PATH'))
NSFW_TAG = getenv('NSFW_TAG')
# What default term(s) shall be used when none are provided?
DEFAULT_TERMS = f'-{NSFW_TAG}'
TEMP = Path(getenv('TEMP_PATH'))

T = TypeVar('T')

def browse_post(
    *args,
    **kwargs
) -> SelectPagination:
    """
    Paginates posts by criteria.

    Args:
        direction (str, optional): Sorting direction, asc for ascending
        and desc for descending
        limit (int): Amount of posts per page
        page (int): Page
        sort (str): Post's column to sort by
        terms (str): Tags, caption and attribute selection
    """
    def post_select(stmt: Select[T]) -> Select[T]:
        terms = kwargs.get('terms', DEFAULT_TERMS)
        caption = None

        try:
            # Capture caption text from terms.
            caption = search(CAPTION_PATTERN, terms)[1]
            terms = sub(CAPTION_PATTERN, '', terms)
        except TypeError:
            pass

        # Capture attribute selectors.
        attrs: list[str] = findall(ATTR_PATTERN, terms)
        terms = sub(ATTR_PATTERN, '', terms)

        # Get tags.
        tags: list[str] = findall(TAG_PATTERN, terms)

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
            sign = ''

            if '<' in attr:
                sign = '<'
            elif '>' in attr:
                sign = '>'

            name, value = attr.split(f':{sign}', 1)
            try:
                value = int(value)
            except ValueError as exc:
                pass

            try:
                col = getattr(Post, name)
            # Skip attribute selector that doesn't exist.
            except AttributeError as exc:
                continue

            try:
                value = int(value)
            except ValueError as exc:
                pass

            if (
                value == 0 and name != 'score'
            ) or (isinstance(value, str) and not len(value)):
                # Look for posts that don't have the column set.
                where = or_(col == None, col == '')
            else:
                if sign == '<':
                    where = col < value
                elif sign == '>':
                    where = col > value
                else:
                    where = col == value

            stmt = stmt.where(where)

        # Apply non-NSFW tag if it's not explicitly specified by user.
        if f'-{NSFW_TAG}' not in tags and NSFW_TAG not in tags:
            tags.append(f'-{NSFW_TAG}')

        # Apply tag selection.

        # Handle showing/hiding removed posts.
        removed_value = Post.removed == False

        if 'removed' in tags:
            removed_value = Post.removed == True
            tags.remove('removed')

        stmt = stmt.where(removed_value)

        # Handle where a user wants to search for posts with no tags.
        if 'no_tags' in tags:
            stmt = stmt.where(~Post.tags.any())
        else:
            for tag in tags:
                if tag[0] != '-':
                    where = Post.tags.any(Tag.name == tag)
                else:
                    where = ~Post.tags.any(Tag.name == tag[1:])

                stmt = stmt.where(where)

        return stmt

    return browse_element(Post, post_select, *args, **kwargs)

def count_all() -> int:
    """
    Returns count of all Posts who aren't marked removed.
    """
    return db.session.scalar(
        select(func.count(Post.id))
        .where(Post.removed == False)
    )

def create_post(
    author: User,
    path: Path,
    directory: Optional[str] = None,
    op: Optional[str] = None,
    src: Optional[str] = None,
    caption: Optional[str] = None,
    tags: Optional[str] = None
) -> Post:
    """
    Creates and returns post.

    Args:
        author: Post's owner
        path: Temporary path to file
        directory: What directory should the post be stored at
        op: Original author of the post
        src: Source
        caption: Post's caption or title
        tags: Space separated tags

    Returns:
        Post ready to commit
    """
    post = Post()

    # Gather metadata about the post.
    dimensions = get_dimensions(path)
    ext = get_extension(path)
    md5 = get_hash(path)
    mime = get_mime(path)
    size = get_size(path)

    if not mime:
        return

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

    thumbnail = create_thumbnail(post)

    try:
        thumbnail.post_id = post.id
    except AttributeError as exc:
        # No thumbnail was made.
        pass

    return post

def delete_post(post: Post, moderator: User, reason: str) -> None:
    """
    Deletes given post.

    Args:
        post
    """
    log = create_log(post, moderator, reason)

def perma_delete_post(post: Post | int) -> None:
    """
    Permanently marks post as deleted, this is an irreversible action.

    Args:
        post: Post to delete
    """
    if isinstance(post, int):
        post = get_post(post)
    
    try:
        db.session.delete(post.thumbnail)
    except UnmappedInstanceError as exc:
        # Some posts may not have a thumbnail and it's alright.
        pass

    db.session.delete(post)

def get_dimensions(path: Path) -> tuple[int, int]:
    """
    Obtains X and Y coordinates of a media path.
    """
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
    """
    Obtains path's extension.

    Returns:
        str: File extension e.g mp4
    """
    return path.suffix[1:]

def get_hash(path: Path) -> str:
    """
    Obtain a path's MD5 hash sum.

    Returns:
        str: MD5
    """
    with path.open('rb') as stream:
        return _md5(stream.read()).hexdigest()

def get_generic_mime(path: Path) -> str:
    """
    Obtains a MIME type for the path.

    Returns:
        str: MIME type generated by magic C library
    """
    return from_file(str(path), mime = True)

def get_mime(path: Path) -> Optional[str]:
    probe_output = ffmpeg.probe(str(path))

    try:
        format_name = probe_output['format']['format_name']
    except KeyError as exc:
        # Could the file be malformed?
        return

    # There can be multiple MIMEs involved with 'image2' demuxer.
    # Map by the file extension.
    if format_name == 'image2':
        match path.suffix[1:].lower():
            case 'gif':
                return 'image/gif'

            case 'jpg':
                return 'image/jpeg'

            case 'jpeg':
                return 'image/jpeg'

            case 'png':
                # image2 is tied to image/png in the dictionary.
                pass

    return MIME_MAP.get(format_name, get_generic_mime(path))

def get_post(post_id: int | str) -> Optional[Post]:
    """
    Queries for a post by its ID or MD5.

    Args:
        post_id: The ID/MD5 of a post you wish to see

    Returns:
        Post
    """
    return db.session.scalar(
        select(Post).where(or_(
            Post.id.is_(post_id),
            Post.md5.is_(post_id)
        ))
    )

def get_size(path: Path) -> int:
    """
    Obtain the amount of bytes in a path.

    Returns:
        int
    """
    with path.open('rb') as stream:
        stream.seek(0, 2)

        return stream.tell()

def move_post(post: Post, directory: str) -> None:
    """
    Moves post file to new directory.

    Args:
        post: Post to move
        directory: Directory name
    """
    original_path = post.path

    new_dir = CONTENT_PATH / Path(directory)
    new_dir.mkdir(exist_ok = True, parents = True)
    new_path = new_dir / post.name

    if new_path != original_path:
        copy(original_path, new_path)
        original_path.unlink(missing_ok = True)

    post.directory = directory
    db.session.commit()

def process_filename(filename: str) -> str:
    """
    Removes non-alphanumeric characters from filename.

    Args:
        filename: Filename
    """
    return sub(NONALPHA, '', filename)

def replace_post(post: Post, file: FileStorage) -> Post:
    """
    Replaces given Post with new file.

    Args:
        post: Post to replace
        path: New file's Path object

    Returns:
        Post
    """
    path = save_file(file)
    md5 = get_hash(path)

    # Ignore the same file being uploaded.
    if md5 == post.md5:
        return

    prev_path = post.path
    dimensions = get_dimensions(path)
    ext = get_extension(path)
    mime = get_mime(path)
    size = get_size(path)

    try:
        post.height = dimensions[1]
        post.width = dimensions[0]
    except TypeError as exc:
        pass

    post.ext = ext
    post.md5 = md5
    post.mime = mime
    post.size = size

    if post.thumbnail:
        db.session.delete(post.thumbnail)
        db.session.flush()

    post.path.parent.mkdir(parents = True, exist_ok = True)
    copy(path, post.path)
    path.unlink(missing_ok = True)
    prev_path.unlink(missing_ok = True)

    thumb = create_thumbnail(post)

    if thumb:
        thumb.post_id = post.id
        thumb.post = post

    return post

def save_file(file: FileStorage) -> Path:
    """
    Saves given file with filename processing before upload.

    Args:
        file: File to save

    Returns:
        Path: Saved file path
    """
    filename = process_filename(file.filename)

    temp_path = TEMP / filename
    file.save(temp_path)

    return temp_path