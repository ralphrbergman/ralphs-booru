from apiflask import Schema
from apiflask.fields import DateTime, String

class TagOut(Schema):
    name = String(required = True)
    created_at = DateTime(attribute = 'created', required = True)
