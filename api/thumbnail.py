from enum import Enum
from os import getenv
from pathlib import Path
from typing import Optional

import ffmpeg
from PIL import Image

from db import db, Post, Thumbnail

TEMP = Path(getenv('TEMP_PATH'))

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
        post: Post to capture thumbnail of.
    """
    temp_f = generate_thumbnail(post)
    alpha = is_alpha_used(temp_f)

    if not alpha:
        try:
            # Create new thumbnail in MJPEG container to minimize storage cost.
            temp_f.unlink(missing_ok = True)
        except AttributeError as exception:
            pass

        temp_f = generate_thumbnail(post, ThumbnailType.JPEG)

    thumb = Thumbnail(post = post)

    try:
        with temp_f.open('rb') as stream:
            thumb.data = stream.read()
    except AttributeError as exception:
        # No thumbnail was made.
        return

    temp_f.unlink(missing_ok = True)
    db.session.add(thumb)

    return thumb

def generate_thumbnail(
    post: Post,
    ext: ThumbnailType = ThumbnailType.PNG
) -> Optional[Path]:
    """
    Generate and return thumbnail based off the content's embedded
    cover art or the generic first frame.

    Args:
        post
        ext
    """
    out = TEMP / (post.md5 + f'.{ext.value}')
    post_path = str(post.path)

    # Find out which video stream has an embedded thumbnail.
    try:
        probe_data = ffmpeg.probe(post_path)
    except ffmpeg.Error as exception:
        return

    index: Optional[int] = None

    for stream in probe_data['streams']:
        if stream.get('disposition', {}).get('attached_pic') == 1:
            index = stream['index']
            break

    stream = ffmpeg.input(post_path)[str(index)]

    # Specify muxer.
    stream = ffmpeg.filter(
        stream,
        'format',
        pix_fmts = 'rgba' if ext == ThumbnailType.PNG else 'yuvj420p'
    )
    # Specify dimensions.
    stream = ffmpeg.filter(stream, 'scale', h = HEIGHT_EXPR, w = WIDTH_EXPR)

    try:
        ffmpeg.output(
            stream,
            str(out),
            frames = '1',
            loglevel = 'quiet'
        ).run(
            overwrite_output = True
        )
    except ffmpeg.Error as exception:
        # File isn't visual.
        return

    return out

def is_alpha_used(path: Path) -> bool:
    """
    Return True if the thumbnail path has transparency
    and requires a PNG container.

    Args:
        path
    """
    # TODO:
    # Document the code and what it does for what purpose.
    try:
        image = Image.open(path)
    except AttributeError:
        # No path passed.
        return False

    if image.mode == 'P':
        if 'transparency' in image.info:
            image = image.convert('RGBA')
        else:
            image.close()
            return False
    
    if image.mode not in ('LA', 'RGBA'):
        image.close()
        return False

    alpha_channel = image.getchannel('A')
    min_a, max_a = alpha_channel.getextrema()

    if min_a == 255 and max_a == 255:
        image.close()
        return False

    image.close()
    return True
