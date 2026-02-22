from enum import Enum
from logging import getLogger
from os import getenv
from pathlib import Path
from typing import Optional

import ffmpeg
from PIL import Image

from db import db, Post, Thumbnail

TEMP = Path(getenv('TEMP_PATH'))

# Define how large thumbnails should be in pixels.
TARGET = getenv('TARGET_SIZE')
# Use the largest axis for target.
HEIGHT_EXPR = f'if(gt(iw, ih), {TARGET}, -1)'
WIDTH_EXPR = f'if(gt(iw, ih), -1, {TARGET})'

logger = getLogger('app_logger')

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
    logger.debug(f'Generated PNG thumbnail: {temp_f}')

    if not alpha:
        # Create new thumbnail in MJPEG container to minimize storage cost.
        try:
            temp_f.unlink(missing_ok = True)
        except AttributeError as exception:
            pass

        temp_f = generate_thumbnail(post, ThumbnailType.JPEG)
        logger.debug(
            f'Generated JPEG thumbnail: {temp_f} '\
            'cause it doesn\'t require transparency.'
        )

    thumb = Thumbnail(post = post)

    try:
        with temp_f.open('rb') as stream:
            thumb.data = stream.read()
    except AttributeError as exception:
        logger.debug('No thumbnail was made.')
        return

    temp_f.unlink(missing_ok = True)
    db.session.add(thumb)

    logger.info(f'Created thumbnail for post #{post.id}')
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
    except ffmpeg.Error:
        logger.error(
            f'Can\'t probe non-visual file: {post_path}'
        )
        return

    index: Optional[int] = None

    for stream in probe_data['streams']:
        if stream.get('disposition', {}).get('attached_pic') == 1:
            index = stream['index']
            logger.debug(
                f'Found visual stream: {index}/{len(probe_data['streams'])}'
            )
            break

    stream = ffmpeg.input(post_path)[str(index)]

    # Specify muxer.
    stream = ffmpeg.filter(
        stream,
        'format',
        pix_fmts = 'rgba' if ext == ThumbnailType.PNG else 'yuvj420p'
    )
    logger.debug(
        'Using PNG format for thumbnail'
        if ext == ThumbnailType.PNG else
        'Using JPEG format for thumbnail'
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
        logger.warning(f'Path: {post_path} isn\'t a visual file.')
        return

    logger.debug(f'Generated thumbnail: {out}')
    return out

def is_alpha_used(path: Path) -> bool:
    """
    Return True if the thumbnail path has transparency
    and requires a PNG container.

    Args:
        path
    """
    try:
        image = Image.open(path)
    except AttributeError:
        logger.error(f'Can\'t work with path: {path} in alpha checking.')
        return False

    if image.mode == 'P':
        if 'transparency' in image.info:
            image = image.convert('RGBA')
        else:
            image.close()
            logger.warning(
                f'Path: {path} is palette-based and lacks transparency data.'
            )

            return False

    if image.mode not in ('LA', 'RGBA'):
        image.close()
        logger.warning(
            f'Required Alpha channel (RGBA/LA) not found for path: {path}'
        )

        return False

    alpha_channel = image.getchannel('A')
    min_a, max_a = alpha_channel.getextrema()

    if min_a == 255 and max_a == 255:
        image.close()
        logger.warning(
            f'Path: {path} doesn\'t have any pixels that use transparency'
        )

        return False

    image.close()
    return True
