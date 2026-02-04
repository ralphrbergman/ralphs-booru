from apiflask import Schema
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf

class ScoreIn(Schema):
    """ Represents an inbound score object. """
    target_id = Integer(required = True)
    target_type = String(required = True, validate = Length(max = 10))
    value = Integer(required = True, validate = OneOf(
        (-1, 1),
        error = 'Score must be a -1 or 1'
    ))

class ScoreOut(ScoreIn):
    """ Represents an outbound score object. """
    user_id = Integer(required = True)
