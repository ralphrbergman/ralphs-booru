from apiflask import Schema
from apiflask.fields import DateTime, File, Integer, List, Nested, String
from apiflask.validators import FileType, Length

from .thumbnail import ThumbnailOut

class FileIn(Schema):
    files = List(File(required = True, validate = [
        FileType([ '.gif', '.jpg', '.jpeg', '.mp3', '.mp4', '.png', '.webm', '.webp' ]) 
    ]),
        validate = [ Length(min = 1, max = 10) ]
    )

class PostIn(Schema):
    post_id = Integer(required = True)

class PostsIn(Schema):
    posts = List(Integer, required = True)

    caption = String(required = False)
    directory = String(required = False)
    op = String(required = False)
    source = String(attribute = 'src', required = False)

    add_tags = List(String(), required = False)
    rem_tags = List(String(), required = False)
    tags = List(String(), required = False)

class TagOut(Schema):
    name = String(required = True)
    created_at = DateTime(attribute = 'created', required = True)

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

class PostsOut(Schema):
    posts = Nested(PostOut, many = True)
