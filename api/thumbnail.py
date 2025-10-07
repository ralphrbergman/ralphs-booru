from enum import Enum
from os import getenv
from pathlib import Path
from typing import Optional

import ffmpeg
from sqlalchemy.exc import IntegrityError

from db import db, Post, Thumbnail

TEMP = Path(getenv('TEMP'))

# Define how large thumbnails should be in pixels.
TARGET = 250
# Use the largest axis for target.
HEIGHT_EXPR = f'if(gt(iw, ih), {TARGET}, -1)'
WIDTH_EXPR = f'if(gt(iw, ih), -1, {TARGET})'

class ThumbnailType(Enum):
    """
    Represents a file extension enum of a thumbnail.
    """
    JPEG = 'jpg'
    PNG = 'png'

def create_thumbnail(post: Post) -> Thumbnail:
    """
    Creates and returns thumbnail object that represents a post's thumbnail.

    Args:
        post (Post): Post to capture thumbnail of.

    Returns:
        Thumbnail
    """
    temp_f = generate_thumbnail(post)

    thumb = Thumbnail()

    try:
        with temp_f.open('rb') as stream:
            thumb.data = stream.read()
    except AttributeError as exc:
        # No thumbnail was made.
        return

    temp_f.unlink(missing_ok = True)

    thumb.post_id = post.id

    db.session.add(thumb)
    try:
        db.session.commit()
    except IntegrityError as exc:
        # Post already has a thumbnail.
        db.session.rollback()

    return thumb

def generate_thumbnail(post: Post, ext: ThumbnailType = ThumbnailType.PNG) -> Optional[Path]:
    """
    Generate and return thumbnail based off the content's embedded
    cover art or the generic first frame.

    Args:
        post (Post)
        ext (ThumbnailType)

    Returns:
        Path
    """
    out = TEMP / (post.md5 + f'.{ext.value}')
    post_path = str(post.path)

    # Find out which video stream has an embedded thumbnail.
    try:
        probe_data = ffmpeg.probe(post_path)
    except ffmpeg.Error as exc:
        return

    index: Optional[int] = None

    for stream in probe_data['streams']:
        if stream.get('disposition', {}).get('attached_pic') == 1:
            index = stream['index']
            break

    stream = ffmpeg.input(post_path)[str(index)]

    # Specify muxer.
    stream = ffmpeg.filter(stream, 'format', pix_fmts = 'rgba' if ext == ThumbnailType.PNG else 'mjpeg')
    # Specify dimensions.
    stream = ffmpeg.filter(stream, 'scale', h = HEIGHT_EXPR, w = WIDTH_EXPR)

    try:
        ffmpeg.output(
            stream,
            str(out),
            frames = '1'
        ).run(
            overwrite_output = True
        )
    except ffmpeg.Error as exc:
        # File isn't visual.
        return

    return out
