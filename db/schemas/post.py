from apiflask import Schema
from apiflask.fields import Boolean, DateTime, Integer, List, Nested, String
from apiflask.validators import Length

from .base import AuthorSchema
from .file import FileIn

class PostIn(Schema):
    """ Represents an inbound post metadata object. """
    op = String()
    src = String()
    caption = String()

class PostDeleteIn(Schema):
    """ Represents an inbound post deletion reason object. """
    reason = String(required = True, validate = Length(min = 15, max = 150))

class PostFormIn(FileIn, PostIn):
    """ Represents an inbound post metadata for HTML forms object. """
    directory = String()

class PostOut(AuthorSchema, PostIn):
    """ Represents an outbound post object. """
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
