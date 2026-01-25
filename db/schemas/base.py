from apiflask import Schema
from apiflask.fields import DateTime, Integer, Nested

class BaseSchema(Schema):
    """ Represents a base schema used across all schemas. """
    id = Integer(required = True)
    created = DateTime(required = True)

class AuthorSchema(BaseSchema):
    """ Represents a base schema but with added author schema. """
    author = Nested(
        'UserOut',
        exclude = ('posts', 'comments'),
        required = True
    )

class PostMixin():
    """ Represents a mixin that adds a post feature. """
    post = Nested('PostOut', exclude = ('author',))

class ScoreMixin():
    """ Represents a mixin that adds a total score feature. """
    score = Integer(required = True)
