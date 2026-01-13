from apiflask import Schema
from apiflask.fields import DateTime, Integer, Nested, String

from .tag import TagOut
from .thumbnail import ThumbnailOut

class PostIn(Schema):
    post_id = Integer(required = True)

class PostOut(PostIn):
    created_at = DateTime(attribute = 'created', required = True)
    modified_at = DateTime(attribute = 'modified')

    id = Integer(required = True)
    author = Integer(attribute = 'author_id', required = True)

    op = String()
    source = String(attribute = 'src')

    caption = String()
    tags = Nested(TagOut, many = True)

    directory = String()
    md5 = String(required = True)
    ext = String(required = True)

    cat = String(required = True)
    mime = String(required = True)
    size = Integer(required = True)

    height = Integer()
    width = Integer()

    dimensions = String()
    name = String()
    thumbnail = Nested(ThumbnailOut)
    url = String(attribute = 'uri', required = True)
    view_url = String(attribute = 'view_uri', required = True)
