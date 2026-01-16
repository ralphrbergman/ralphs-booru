from apiflask import Schema
from apiflask.fields import Integer, String
from apiflask.validators import Length

class ScoreIn(Schema):
    target_id = Integer(required = True)
    target_type = String(validate = Length(max = 10))

class ScoreOut(ScoreIn):
    decision = String(required = True)
    user_id = Integer(required = True)
