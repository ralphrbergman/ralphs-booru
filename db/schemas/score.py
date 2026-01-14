from apiflask import Schema
from apiflask.fields import Integer, String

class ScoreIn(Schema):
    post_id = Integer(required = True)

class ScoreOut(ScoreIn):
    decision = String(required = True)
    user_id = Integer(required = True)
