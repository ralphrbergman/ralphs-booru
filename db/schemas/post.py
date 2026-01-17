from apiflask import Schema
from apiflask.fields import Boolean, DateTime, Integer, List, Nested, String

from .base import AuthorSchema
from .file import FileIn

class PostIn(Schema):
    op = String()
    src = String()
    caption = String()

class PostFormIn(FileIn, PostIn):
    directory = String()

class PostOut(AuthorSchema, PostIn):
    modified = DateTime()
    tags = List(Nested('TagOut', exclude = ('posts',)))
    md5 = String(required = True)
    ext = String(required = True)
    mime = String(required = True)
    height = Integer()
    width = Integer()
    comments = List(Nested('CommentOut', exclude = ('post',)))
    cat = String(required = True)
    dimensions = String(required = True)
    disk_size = String(required = True)
    name = String(required = True)
    nsfw = Boolean(required = True)
    url = String(attribute = 'uri', required = True)
