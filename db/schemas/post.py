from apiflask import Schema
from apiflask.fields import DateTime, File, Integer, List, Nested, String
from apiflask.validators import FileType, Length

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

    caption = String(load_default = None)
    directory = String(load_default = None)
    op = String(load_default = None)
    source = String(attribute = 'src', load_default = None)
    tags = List(String(), load_default = None)

class TagOut(Schema):
    name = String(required = True)
    created_at = DateTime(attribute = 'created', required = True)

class PostOut(PostIn):
    created_at = DateTime(attribute = 'created', required = True)
    modified_at = DateTime(attribute = 'modified')

    author = Integer(attribute = 'author_id', required = True)

    op = String()
    source = String(attribute = 'src')

    caption = String()
    tags = Nested(TagOut, many = True)

    directory = String()
    md5 = String(required = True)
    ext = String(required = True)

    mime = String(required = True)
    size = Integer(required = True)

    height = Integer()
    width = Integer()

    dimensions = String()
    name = String()
    view_url = String(attribute = 'view_uri', required = True)

class PostsOut(Schema):
    posts = Nested(PostOut, many = True)
