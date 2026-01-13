from apiflask import Schema
from apiflask.fields import Integer, String

class ThumbnailOut(Schema):
    id = Integer(required = True)
    post_id = Integer(required = True)
    view_url = String(attribute = 'view_uri', required = True)
